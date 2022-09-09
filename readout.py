import pyglet


def hex_to_rgb(hex_string):
    return tuple(int(hex_string[i:i+2], 16) for i in (0, 2, 4))


class Readout():
    def __init__(self, frame, heading_position, animation_manager, batch, group_dict):
        self.animation_manager = animation_manager
        self.animation_manager.readout = self
        self.heading_objects = []
        self.readout_objects = []
        self.visible_objects = []
        self.next_reveal_index = 0
        self.last_reveal_dt = 0
        
        # Get times etc. in order they should appear on screen
        self.sector_index = []
        self.anim_times = []
        self.tlas = []
        self.colors = []
        self.cum_strings = []
        self.sector_strings = []
        for i, s in enumerate(range(1, 4)):
            frame.sort_values(f"Sector{s}AnimTime", inplace=True)
            self.sector_index.extend([i] * len(frame.index))
            self.anim_times.extend(list(frame[f"Sector{s}AnimTime"]))
            self.tlas.extend(list(frame["Tla"]))
            self.colors.extend(list(frame["TeamColour"]))
            self.cum_strings.extend(list(frame[f"CumSector{s}String"]))
            self.sector_strings.extend(list(frame[f"Sector{s}String"]))

        # Create readout text etc., set invisible - update loop will set visible as needed
        position = None
        row_num = 0
        row_height = 16
        for i in range(len(self.sector_index)):
            if i == 0 or self.sector_index[i] > self.sector_index[i-1]: 
                position = (heading_position[0], heading_position[1] - row_height)
                row_num = 0
            else:
                position = (position[0], position[1] - row_height)
                row_num += 1

            bg_color = (255, 255, 255) if row_num % 2 == 0 else (210, 210, 210)

            rect = pyglet.shapes.Rectangle(position[0], position[1], 200, row_height, bg_color, batch=batch, group=group_dict["GUI_back"])
            rect.opacity = 180
            color_patch = pyglet.shapes.Rectangle(position[0], position[1], 10, row_height, hex_to_rgb(self.colors[i]), batch=batch, group=group_dict["GUI_mid"])
            tla_label = pyglet.text.Label(
                text=self.tlas[i], 
                font_name="TitilliumWeb-Regular", 
                font_size=10, 
                color=(0, 0, 0, 255),
                x=position[0] + 10,
                y=position[1] + row_height/2,
                anchor_y="center",
                batch=batch,
                group=group_dict["GUI_mid"]
            )
            lap_string = pyglet.text.Label(
                text=self.cum_strings[i], 
                font_name="TitilliumWeb-Regular", 
                font_size=10, 
                color=(0, 0, 0, 255),
                x=position[0] + 50,
                y=position[1] + row_height/2,
                anchor_y="center",
                batch=batch,
                group=group_dict["GUI_mid"]
            )
            sector_string = pyglet.text.Label(
                text=self.sector_strings[i], 
                font_name="TitilliumWeb-Regular", 
                font_size=10, 
                color=(0, 0, 0, 255),
                x=position[0] + 125,
                y=position[1] + row_height/2,
                anchor_y="center",
                batch=batch,
                group=group_dict["GUI_mid"]
            )


            objects = [rect, color_patch, tla_label, lap_string, sector_string]

            for ob in objects:
                ob.visible = False

            self.readout_objects.append(objects)

        # Heading
        heading_bg = pyglet.shapes.Rectangle(heading_position[0], heading_position[1], 200, row_height, (21, 21, 30), batch, group_dict["GUI_back"])
        heading_lap = pyglet.text.Label(
            text="Lap time",
            font_name="TitilliumWeb-Regular",
            font_size=10,
            color=(255, 255, 255, 255),
            x=heading_position[0] + 50,
            y=heading_position[1] + row_height/2,
            anchor_y="center",
            batch=batch,
            group=group_dict["GUI_mid"]
        )
        heading_sector = pyglet.text.Label(
            text="Sector time",
            font_name="TitilliumWeb-Regular",
            font_size=10,
            color=(255, 255, 255, 255),
            x=heading_position[0] + 125,
            y=heading_position[1] + row_height/2,
            anchor_y="center",
            batch=batch,
            group=group_dict["GUI_mid"]
        )

        self.heading_objects = [heading_bg, heading_lap, heading_sector]
        for ob in self.heading_objects:
            ob.visible = False


    def update_screen_position(self, cumulative_dt):
        # Set each collection of objects visible as animation time is reached
        if self.next_reveal_index < len(self.anim_times) and self.anim_times[self.next_reveal_index] <= cumulative_dt:
            if len(self.visible_objects) == 0:
                for ob in self.heading_objects:
                    ob.visible = True
                    self.visible_objects.append(ob)
            for ob in self.readout_objects[self.next_reveal_index]:
                ob.visible = True
                self.visible_objects.append(ob)
            self.next_reveal_index += 1
            self.last_reveal_dt = cumulative_dt

        # Hide readouts once none have been added for a few seconds
        if self.last_reveal_dt < cumulative_dt - 10.0:
            for ob in self.visible_objects:
                ob.visible = False
            self.visible_objects.clear()


    def restart(self):
        self.next_reveal_index = 0
        for ob in self.visible_objects:
            ob.visible = False
        self.visible_objects.clear()
            