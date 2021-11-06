"""Generate a KiCad project from a Keyboard Leyout Editor json input layout"""
import datetime
import functools
import json
import math
import os
import sys
from typing import List, Tuple

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from kle_pcbgen import MAX_COLS, MAX_ROWS, __version__
from kle_pcbgen.models import Key, Keyboard


@functools.lru_cache()
def unit_width_to_available_footprint(unit_width: float) -> str:
    """Convert a key width in standard keyboard units to the width of the kicad
    footprint to use"""

    # This may not be the appropriate size for everything >= 6.25, but this
    # is what we have
    width = "6.25"
    if unit_width < 1.25:
        width = "1.00"
    elif unit_width < 1.5:
        width = "1.25"
    elif unit_width < 1.75:
        width = "1.50"
    elif unit_width < 2:
        width = "1.75"
    elif unit_width < 2.25:
        width = "2.00"
    elif unit_width < 2.75:
        width = "2.25"
    elif unit_width < 6.25:
        # This may not be the appropriate size for everything between 2.75 and
        # 6.25, but this is what we have
        width = "2.75"
    return width


class KLEPCBGenerator:
    """KLE PCB Generator"""

    def __init__(self, infile: str, outname: str) -> None:
        """Set-up directories"""
        self.jinja_env = Environment(
            loader=FileSystemLoader(["configuration/templates"]),
            undefined=StrictUndefined,
            autoescape=False,
        )
        self.keyboard = Keyboard()
        self.nets = []  # type: List[str]
        self.infile = infile
        self.outname = outname
        self.outpath = os.path.join(
            outname, os.path.basename(os.path.normpath(self.outname))
        )

    def generate_kicadproject(self) -> None:
        """Generate the kicad project. Main entry point"""

        if not os.path.exists(self.outname):
            os.mkdir(self.outname)

        self.read_kle_json()
        self.generate_rows_and_columns()
        self.generate_schematic()
        self.generate_layout()
        self.generate_project()

    def read_kle_json(self) -> None:
        """Read the provided KLE input file and create a list of all the keyswitches that should
        be on the board"""

        print(f"Reading input file '{self.infile}' ...")

        with open(self.infile, encoding="latin-1") as read_file:
            kle_json = json.load(read_file)

        # First create a list of switches, each with its own X,Y coordinate
        current_x = 0.0
        current_y = 0.0
        key_num = 0
        key_rotation = 0
        for row in kle_json:
            if isinstance(row, list):
                # Default keysize is 1x1
                key_width = 1
                key_height = 1
                # Extract all keys in a row
                for item in row:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if key == "x":
                                current_x += value
                            elif key == "y":
                                current_y += value
                            elif key == "w":
                                key_width = value
                            elif key == "h":
                                key_height = value
                            elif key == "r":
                                key_rotation = value
                    elif isinstance(item, str):
                        key = Key(
                            num=key_num,
                            x_unit=current_x + key_width / 2,
                            y_unit=current_y + key_height / 2,
                            legend=item,
                            width=key_width,
                            height=key_height,
                            rotation=key_rotation,
                        )
                        self.keyboard.append(key)

                        current_x += key_width
                        key_num += 1
                        key_width = 1
                        key_height = 1
                    else:
                        print(f"Found unexpected JSON element ({item}). Exiting")
                        sys.exit()
                current_y += 1
                current_x = 0
            else:
                # Found the meta-info block.
                if "name" in row:
                    self.keyboard.name = row["name"]
                if "author" in row:
                    self.keyboard.author = row["author"]

    def generate_rows_and_columns(self) -> None:
        """Group keys in rows and columns based on the position of the center of the switch in a
        grid"""

        print("Grouping keys in rows and columns ... ")

        # For each key in the board, determine the X,Y of the center of the key. This determines
        # the row/column a key is in
        keys_in_row = [0] * MAX_ROWS
        for index, key in enumerate(self.keyboard):
            centery = key.y_unit
            row = math.floor(centery)

            if row > MAX_ROWS - 1:
                sys.exit(
                    "ERROR: Key placement produced too many rows. klepcbgen currently cannot generate a valid KiCad project for this keyboard layout.\nExiting ..."
                )

            self.keyboard.add_key_to_row(row, index)
            self.keyboard[index].row = row

            col = keys_in_row[row]
            keys_in_row[row] += 1

            if col > MAX_COLS - 1:
                sys.exit(
                    "ERROR: Key placement produced too many columns. klepcbgen currently cannot generate a valid KiCad project for this keyboard layout.\nExiting ..."
                )

            self.keyboard.add_key_to_col(col, index)
            self.keyboard[index].col = col

    def place_schematic_components(self) -> str:
        """Place schematic components determined by the layout(keyswitches and diodes)"""
        switch_tpl = self.jinja_env.get_template("schematic/keyswitch.tpl")

        component_count = 0
        components_section = ""

        # Place keyswitches and diodes
        for key in self.keyboard:
            placement_x = int(600 + key.x_unit * 800)
            placement_y = int(800 + key.y_unit * 500)

            components_section += (
                switch_tpl.render(
                    num=component_count,
                    x=placement_x,
                    y=placement_y,
                    rowNum=key.row,
                    colNum=key.col,
                    keywidth=unit_width_to_available_footprint(key.width),
                )
                + "\n"
            )
            component_count += 1

        return components_section

    def generate_schematic(self) -> None:
        """Generate schematic"""

        print("Generating schematic ...")
        schematic = self.jinja_env.get_template("schematic/schematic.tpl")
        with open(f"{self.outpath}.sch", "w+", newline="\n") as out_file:
            out_file.write(
                schematic.render(
                    components=self.place_schematic_components(),
                    controlcircuit=self.jinja_env.get_template(
                        "schematic/controlcircuit.tpl"
                    ).render(),
                    title=self.keyboard.name,
                    author=self.keyboard.author,
                    date=datetime.datetime.utcnow(),
                    comment=f"Generated by kle_pcbgen v{__version__}",
                )
            )

    def place_layout_components(self) -> Tuple[str, int]:
        """Place footprint components"""
        switch = self.jinja_env.get_template("layout/keyswitch.tpl")
        diode = self.jinja_env.get_template("layout/diode.tpl")
        component_count = 0
        components_section = ""

        # Place keyswitches, diodes, vias and traces
        key_pitch = 19.05
        diode_offset = [-6.35, 8.89]

        for key in self.keyboard:
            # Place switch
            ref_x = -9.525 + key.x_unit * key_pitch
            ref_y = -9.525 + key.y_unit * key_pitch
            components_section += (
                switch.render(
                    num=component_count,
                    x=ref_x,
                    y=ref_y,
                    diodenetnum=key.diodenetnum,
                    diodenetname=f'"Net-(D{key.num}-Pad2)"',
                    colnetnum=key.colnetnum,
                    colnetname=f"/Col_{key.col}",
                    rotation=key.rotation,
                    keywidth=unit_width_to_available_footprint(key.width),
                )
                + "\n"
            )

            # Place diode
            diode_x = ref_x + diode_offset[0]
            diode_y = ref_y + diode_offset[1]
            components_section += (
                diode.render(
                    num=component_count,
                    x=diode_x,
                    y=diode_y,
                    diodenetnum=key.diodenetnum,
                    diodenetname=f'"Net-(D{key.num}-Pad2)"',
                    rownetnum=key.rownetnum,
                    rownetname=f"/Row_{key.row}",
                )
                + "\n"
            )

            component_count += 1

        return components_section, component_count

    def define_nets(self) -> None:
        """Define all the nets for this layout"""
        self.nets.append("GND")
        self.nets.append("VCC")
        self.nets.append('"Net-(C6-Pad1)"')
        self.nets.append('"Net-(C7-Pad1)"')
        self.nets.append('"Net-(C8-Pad1)"')
        self.nets.append('"Net-(J1-Pad4)"')
        self.nets.append('"Net-(J1-Pad3)"')
        self.nets.append('"Net-(J1-Pad2)"')
        self.nets.append('"Net-(R1-Pad1)"')
        self.nets.append('"Net-(R2-Pad1)"')
        self.nets.append('"Net-(R3-Pad1)"')
        self.nets.append('"Net-(R4-Pad2)"')
        self.nets.append('"Net-(U1-Pad42)"')
        self.nets.append("/Reset")

        # Always declare the max number of row nets, since the control circuit template refers to them
        for row_num in range(MAX_ROWS):
            self.nets.append(f"/Row_{row_num}")

        # Always declare the max number of column nets, since the control circuit template refers to them
        for col_num in range(MAX_COLS):
            self.nets.append(f"/Col_{col_num}")

        for diode_num in range(len(self.keyboard)):
            self.nets.append(f'"Net-(D{diode_num}-Pad2)"')

    def create_layout_nets(self) -> str:
        """Create the list of nets in the layout"""
        addnets = ""
        declarenets = ""

        # Create a declaration and addition for each net
        for idx in range(0, 1 + len(self.nets)):
            try:
                netname = self.nets[idx]
            except IndexError:
                netname = "UNKNOWN"
            declarenets += f"  (net {idx+1} {netname})\n"
            addnets += f"    (add_net {netname})\n"

        # make each key in the board aware in which row/column/diode net it resides
        for idx, row in enumerate(self.keyboard.rows):
            rownetname = f"/Row_{idx}"
            for key_idx in row:
                try:
                    netnum = self.nets.index(rownetname) + 1
                except ValueError:
                    netnum = 0
                self.keyboard[key_idx].rownetnum = netnum

        for idx, col in enumerate(self.keyboard.columns):
            colnetname = f"/Col_{idx}"
            for key_idx in col:
                try:
                    netnum = self.nets.index(colnetname) + 1
                except ValueError:
                    netnum = 0
                self.keyboard[key_idx].colnetnum = netnum

        for idx, _ in enumerate(self.keyboard):
            diodenetname = f'"Net-(D{idx}-Pad2)"'
            try:
                netnum = self.nets.index(diodenetname) + 1
            except ValueError:
                netnum = 0
            self.keyboard[idx].diodenetnum = netnum

        nets = self.jinja_env.get_template("layout/nets.tpl")

        return nets.render(netdeclarations=declarenets, addnets=addnets)

    def generate_layout(self) -> None:
        """Generate layout"""

        print("Generating PCB layout ...")

        self.define_nets()
        nets = self.create_layout_nets()

        components, numcomponents = self.place_layout_components()
        layout = self.jinja_env.get_template("layout/layout.tpl")
        controlcircuit = self.jinja_env.get_template("layout/controlcircuit.tpl")
        with open(f"{self.outpath}.kicad_pcb", "w+", newline="\n") as out_file:
            out_file.write(
                layout.render(
                    modules=components,
                    nummodules=numcomponents,
                    nets=nets,
                    numnets=len(self.nets),
                    controlcircuit=controlcircuit.render(nets=self.nets, startnet=0),
                )
            )

    def generate_project(self) -> None:
        """Generate the project file"""
        prj = self.jinja_env.get_template("kicadproject.tpl")
        with open(f"{self.outpath}.pro", "w+", newline="\n") as out_file:
            out_file.write(prj.render())
