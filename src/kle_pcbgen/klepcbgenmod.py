"""Generate a KiCad project from a Keyboard Leyout Editor json input layout"""
import datetime
import json
import os
import sys
import configparser
from typing import List

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from kle_pcbgen import MAX_COLS, MAX_ROWS, __version__
from kle_pcbgen.models import Key, Keyboard



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
        self.settings = {}
        self.parse_config()
        #needs cleanup but assigning net id based on row fixes the weird issues we saw.
        self.net_row_names = {'0': 15,
            '1': 16,
            '2': 17,
            '3': 18,
            '4': 19,
            '5': 20,
            '6': 21,
            '7': 22,
            '8': 23,
            '9': 24}


    def parse_config(self,filename='src/kle_pcbgen/config.yaml'):
        """parse the config.yaml file for values to customize pcb generator"""
        config = configparser.ConfigParser()
        config.sections()
        config.read(filename)
        for key in config['settings']:
            self.settings[key] = config['settings'][key]
        


    def generate_kicadproject(self) -> None:
        """Generate the kicad project. Main entry point"""

        if not os.path.exists(self.outname):
            os.mkdir(self.outname)

        self.read_kle_json()
        self.keyboard.generate_matrix()
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
                        if key_height > 1:
                            print("key_height > 1", key_height)
                        key = Key(
                            number=key_num,
                            x_unit=current_x + key_width / 2,
                            y_unit=current_y + key_height / 2,
                            legend=item.replace("\n", ""),
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

    @property
    def schematic_components(self) -> List[str]:
        """Place schematic components determined by the layout(keyswitches and diodes)"""
        switch_tpl = self.jinja_env.get_template("schematic/keyswitch.tpl")
        components = []

        # Place keyswitches
        for key in self.keyboard:
            print(key.row)
            render = switch_tpl.render(
                num=key.number,
                x=int(600 + key.x_unit * 800),
                y=int(800 + key.y_unit * 500),
                rowNum=key.row,
                colNum=key.column,
                width=key.width,
            )
            components.append(render)
        return components

    def generate_schematic(self) -> None:
        """Generate schematic"""

        print("Generating schematic ...")
        schematic = self.jinja_env.get_template("schematic/schematic.tpl")
        with open(f"{self.outpath}.sch", "w+", newline="\n") as out_file:
            out_file.write(
                schematic.render(
                    components=self.schematic_components,
                    controlcircuit=self.jinja_env.get_template(
                        "schematic/controlcircuit.tpl"
                    ).render(),
                    title=self.keyboard.name,
                    author=self.keyboard.author,
                    date=datetime.datetime.utcnow(),
                    comment=f"Generated by kle_pcbgen v{__version__}",
                )
            )

    @property
    def layout_components(self) -> List[str]:
        """Place footprint components"""
        # add selection for footprint here.
        #TODO: select these templates in config file
        try:
            switch = self.jinja_env.get_template(f"layout/{self.settings['switch_footprint']}.tpl")
        except:
            self.jinja_env.get_template("layout/keyswitch.tpl")
        
        try:
            diode = self.jinja_env.get_template(f"layout/{self.settings['diode']}.tpl")
        except:
            diode = self.jinja_env.get_template("layout/diode.tpl")
        components = []

        # Place keyswitches, diodes, vias and traces
        key_pitchx = float(self.settings['horz_pitch'])
        key_pitchy = float(self.settings['vert_pitch'])
        diode_offset = [0, 4]
        for key in self.keyboard:
            # Place switch
            ref_x = -9.525 + key.x_unit * key_pitchx
            ref_y = -9.525 + key.y_unit * key_pitchy
            render = switch.render(
                key=key,
                x=ref_x,
                y=ref_y,
            )
            components.append(render)
            if self.settings['diode_or'] == 'hor':
                diode_rotation = 0
            elif self.settings['diode_or'] == 'ver':
                diode_rotation = 90
            else:
                diode_rotation = float(self.settings['diode_or'])
            # Place diode
            render = diode.render(
                num=key.number,
                x=ref_x + float(self.settings['diode_x']),
                y=ref_y + float(self.settings['diode_y']),
                diodenetnum=key.diodenetnum,
                diodenetname=f'"Net-(D{key.number}-Pad2)"',
                rownetnum=key.rownetnum,
                rownetname=f"/Row_{key.row}",
                diode_rotate = diode_rotation,
            )
            components.append(render)

        return components

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
            for key in row:
                try:
                    netnum = self.net_row_names[str(key.row)]

                except ValueError:
                    netnum = 0
                key.rownetnum = netnum

        for idx, col in enumerate(self.keyboard.columns):
            colnetname = f"/Col_{idx}"
            for key in col:
                try:
                    netnum = self.nets.index(colnetname) + 1
                except ValueError:
                    netnum = 0
                key.colnetnum = netnum

        for key in self.keyboard:
            diodenetname = f'"Net-(D{key.number}-Pad2)"'
            try:
                netnum = self.nets.index(diodenetname) + 1
            except ValueError:
                netnum = 0
            key.diodenetnum = netnum

        nets = self.jinja_env.get_template("layout/nets.tpl")

        return nets.render(netdeclarations=declarenets, addnets=addnets)

    def generate_layout(self) -> None:
        """Generate layout"""
        print("Generating PCB layout ...")

        self.define_nets()
        nets = self.create_layout_nets()

        layout = self.jinja_env.get_template("layout/layout.tpl")
        controlcircuit = self.jinja_env.get_template("layout/controlcircuit.tpl")
        with open(f"{self.outpath}.kicad_pcb", "w+", newline="\n") as out_file:
            out_file.write(
                layout.render(
                    modules=self.layout_components,
                    nets=nets,
                    controlcircuit=controlcircuit.render(nets=self.nets, startnet=0),
                )
            )

    def generate_project(self) -> None:
        """Generate the project file"""
        prj = self.jinja_env.get_template("kicadproject.tpl")
        with open(f"{self.outpath}.pro", "w+", newline="\n") as out_file:
            out_file.write(prj.render())


