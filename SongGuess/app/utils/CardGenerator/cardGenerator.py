import os
from PIL import Image, ImageFont, ImageDraw
from fpdf import FPDF
from qrcode import QRCode, constants

class CardGenerator:
    def __init__(self):
        self._resolution = 300

        self._card_width = self.in_px(85)
        self._card_height = self.in_px(54)

        self._paper_width = self.in_px(210)
        self._paper_height = self.in_px(297)

        # Data for C32010-25 businees card paper:
        self._paper_top_margin = self.in_px(10)    # Space from the top of the paper to the first card
        self._paper_left_margin = self.in_px(13.5) # Space from the left of the paper to the first card

        self._card_top_spacing = self.in_px(0) # Space between the cards
        self._card_right_spacing = self.in_px(10) # Space between the cards

        self._qr_size = self.in_px(30) # Size of the QR code in mm
        self._qr_text_size = self.in_px(2) # Size of the text below the QR code
        self._show_qr_id = True # Show the QR code ID below the QR code
        self._qr_text_margin = self.in_px(2) # Margin between the QR code and the text below it in mm
        self._outline_width = self.in_px(0.3) # Width of the outline around the card in mm

        self._font_path = os.path.join(os.path.dirname(__file__), 'fonts')

    @property
    def resolution(self) -> int:
        """Resolution in pixels per mm."""
        return self._resolution

    @resolution.setter
    def resolution(self, value : int):
        self._resolution = value

    @property
    def card_width(self) -> int:
        """Card width in px."""
        return self._card_width

    @card_width.setter
    def card_width(self, value: int):
        """Set card width in px."""
        self._card_width = value

    @property
    def card_height(self) -> int:
        """Card height in px."""
        return self._card_height

    @card_height.setter
    def card_height(self, value: int):
        """Set card height in px."""
        self._card_height = value

    @property
    def paper_width(self) -> int:
        """Paper width in px."""
        return self._paper_width

    @paper_width.setter
    def paper_width(self, value: int):
        """Set paper width in px."""
        self._paper_width = value

    @property
    def paper_height(self) -> int:
        """Paper height in px."""
        return self._paper_height

    @paper_height.setter
    def paper_height(self, value: int):
        """Set paper height in px."""
        self._paper_height = value

    @property
    def paper_top_margin(self) -> int:
        """Top margin of the paper in px."""
        return self._paper_top_margin

    @paper_top_margin.setter
    def paper_top_margin(self, value: int):
        """Set top margin of the paper in px."""
        self._paper_top_margin = value

    @property
    def paper_left_margin(self) -> int:
        """Left margin of the paper in px."""
        return self._paper_left_margin

    @paper_left_margin.setter
    def paper_left_margin(self, value: int):
        """Set left margin of the paper in px."""
        self._paper_left_margin = value

    @property
    def card_top_spacing(self) -> int:
        """Spacing between the cards in px."""
        return self._card_top_spacing

    @card_top_spacing.setter
    def card_top_spacing(self, value: int):
        """Set spacing between the cards in px."""
        self._card_top_spacing = value

    @property
    def card_right_spacing(self) -> int:
        """Spacing between the cards in px."""
        return self._card_right_spacing

    @card_right_spacing.setter
    def card_right_spacing(self, value: int):
        """Set spacing between the cards in px."""
        self._card_right_spacing = value

    @property
    def qr_size(self) -> int:
        """Size of the QR code in px."""
        return self._qr_size

    @qr_size.setter
    def qr_size(self, value: int):
        """Set size of the QR code in px."""
        self._qr_size = value

    @property
    def qr_text_size(self) -> int:
        """Size of the text below the QR code in px."""
        return self._qr_text_size

    @qr_text_size.setter
    def qr_text_size(self, value: int):
        """Set size of the text below the QR code in px."""
        self._qr_text_size = value

    @property
    def show_qr_id(self) -> bool:
        """Whether to show the QR code ID below the QR code."""
        return self._show_qr_id

    @show_qr_id.setter
    def show_qr_id(self, value: bool):
        """Set whether to show the QR code ID below the QR code."""
        self._show_qr_id = value

    @property
    def qr_text_margin(self) -> int:
        """Margin between the QR code and the text below it in px."""
        return self._qr_text_margin

    @qr_text_margin.setter
    def qr_text_margin(self, value: int):
        """Set margin between the QR code and the text below it in px."""
        self._qr_text_margin = value

    @property
    def outline_width(self) -> int:
        """Width of the outline around the card in px."""
        return self._outline_width

    @outline_width.setter
    def outline_width(self, value: int):
        """Set width of the outline around the card in px."""
        self._outline_width = value

    def in_px(self, value: float) -> int:
        return int(value * self._resolution / 25.4)

    def in_mm(self, value: float) -> int:
        return int(value / self._resolution * 25.4)
    
    def _generate_qr(self, text):
        qr = QRCode(
            version=1,
            error_correction=constants.ERROR_CORRECT_M,
            box_size=10,
            border=1,
        )
        qr.add_data(text.encode('utf-8-sig'))
        qr.make(fit=True)
        qr_img = qr.make_image(
            fill_color='black',
            back_color="white")
        return qr_img


    def generate_back(self, qr_data: str, show_qr_text: bool = True, outline: bool = False) -> Image.Image:

        qr_data = qr_data.strip().lower()
        img = Image.new(mode='RGB', size=(self._card_width, self._card_height), color=(255, 255, 255))
        qr_img = self._generate_qr(qr_data)
        qr_img = qr_img.resize((self._qr_size, self._qr_size), Image.Resampling.LANCZOS) # type: ignore
        
        x_pos = int(self._card_width / 2) - int(qr_img.width / 2)
        y_pos = int(self._card_height / 2) - int(qr_img.height / 2)

        img.paste(qr_img, (x_pos, y_pos))

        if show_qr_text:
            font = ImageFont.truetype(os.path.join(self._font_path, 'Manrope-Regular.ttf'), self._qr_text_size)
            font_bounding = font.getbbox(qr_data)
            x_pos = int(self._card_width / 2) - int((font_bounding[2] - font_bounding[0]) / 2)
            y_pos = y_pos + int(qr_img.height) + int((font_bounding[3] + font_bounding[1]) / 2) + self._qr_text_margin
            
            draw = ImageDraw.Draw(img)
            draw.text((x_pos, y_pos), qr_data, (0, 0, 0), font=font)

        if outline:
            draw = ImageDraw.Draw(img)
            draw.rectangle(
                [(0, 0), (self._card_width, self._card_height)],
                outline=(0, 0, 0),
                width=self._outline_width
            )

        return img
    
    def generate_front(self, artist: str, title: str, year: str = "1234", qr_id = None, outline:bool = False) -> Image.Image:
        img = Image.new(mode='RGB', size=(self._card_width, self._card_height), color=(255, 255, 255))
        font = ImageFont.truetype(os.path.join(self._font_path, 'Manrope-Regular.ttf'), self.in_px(15))
        year = str(year).strip()
        year_bounding = font.getbbox(year)
        x_pos = int(self._card_width / 2) - int((year_bounding[2] - year_bounding[0]) / 2)
        y_pos = int(self._card_height / 2) - int((year_bounding[3] + year_bounding[1]) / 2) 
        draw = ImageDraw.Draw(img)
        draw.text((x_pos, y_pos), year, (0, 0, 0), font=font)

        font_start_size = 8
        font = ImageFont.truetype(os.path.join(self._font_path, 'Manrope-Regular.ttf'), self.in_px(font_start_size))
        title_bounding = font.getbbox(title)
        while title_bounding[2] > (self._card_width - self.in_px(5)):
            font_start_size -= 0.5
            if font_start_size < 1:
                break # If title is too long, stop size reduction
            font = ImageFont.truetype(os.path.join(self._font_path, 'Manrope-Regular.ttf'), self.in_px(font_start_size))
            title_bounding = font.getbbox(title)  

        x_pos = int(self._card_width / 2) - int((title_bounding[2] - title_bounding[0]) / 2)
        y_pos = self.in_px(3) 
        draw = ImageDraw.Draw(img)
        draw.text((x_pos, y_pos), title, (0, 0, 0), font=font)

        font_start_size = 8
        font = ImageFont.truetype(os.path.join(self._font_path, 'Manrope-Regular.ttf'), self.in_px(font_start_size))
        artist_bounding = font.getbbox(artist)
        while artist_bounding[2] > (self._card_width - self.in_px(5)):
            font_start_size -= 0.5
            if font_start_size < 1:
                break # If title is too long, stop size reduction
            font = ImageFont.truetype(os.path.join(self._font_path, 'Manrope-Regular.ttf'), self.in_px(font_start_size))
            artist_bounding = font.getbbox(artist)  

        x_pos = int(self._card_width / 2) - int((artist_bounding[2] - artist_bounding[0]) / 2)
        y_pos = self._card_height - self.in_px(3) - int(artist_bounding[3])
        draw = ImageDraw.Draw(img)
        draw.text((x_pos, y_pos), artist, (0, 0, 0), font=font)

        if outline:
            draw = ImageDraw.Draw(img)
            draw.rectangle(
                [(0, 0), (self._card_width, self._card_height)],
                outline=(0, 0, 0),
                width=self._outline_width
            )

        if qr_id is not None:
            qr_id = str(qr_id).strip().lower()
            font = ImageFont.truetype(os.path.join(self._font_path, 'Manrope-Regular.ttf'), self._qr_text_size)
            font_bounding = font.getbbox(qr_id)

            img = img.rotate(-90, expand=1)
            rotated_width, rotated_height = img.size
            x_pos = int(rotated_width / 2) - int((font_bounding[2] - font_bounding[0]) / 2)
            y_pos = self.in_px(3)
            draw = ImageDraw.Draw(img)
            draw.text((x_pos, y_pos), qr_id, (0, 0, 0), font=font)   
            img = img.rotate(90, expand=1)         
        return img

    def generate_page(self, images: list[Image.Image], flip: bool = False) -> Image.Image:
        """Generate a page with the given images. If flip is True, place images right-to-left."""
        page_width = self._paper_width
        page_height = self._paper_height

        img = Image.new(mode='RGB', size=(page_width, page_height), color=(255, 255, 255))

        if not flip:
            x_pos = self._paper_left_margin
            y_pos = self._paper_top_margin

            for image in images:
                img.paste(image, (x_pos, y_pos))
                x_pos += image.width + self._card_right_spacing
                if x_pos + image.width > page_width:
                    x_pos = self._paper_left_margin
                    y_pos += image.height + self._card_top_spacing
        else:
            x_pos = page_width - self._paper_left_margin - self._card_width
            y_pos = self._paper_top_margin

            for image in images:
                img.paste(image, (x_pos, y_pos))
                x_pos -= image.width + self._card_right_spacing
                if x_pos < self._paper_left_margin:
                    x_pos = page_width - self._paper_left_margin - self._card_width
                    y_pos += image.height + self._card_top_spacing

        return img
    
    def generate_pdf(self, pages: list[Image.Image], filename: str):
        
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        for page in pages:
            pdf.add_page()
            pdf.image(page, 0, 0, self.in_mm(self._paper_width), self.in_mm(self._paper_height)) 
        pdf.output(filename)

    def pdf_from_songs(self, list_of_songs: list[dict], filename: str, outlines = "NONE"):
        """
        Generate a PDF from a list of songs.
        Each song should be a dictionary with keys: 'name', 'song', 'year', 'token'.
        """
        #split list to chunks of 10 songs
        song_list_chunks = [list_of_songs[i:i + 10] for i in range(0, len(list_of_songs), 10)]
        pages = []
        for song_chunk in song_list_chunks:
            images = []    
            for song in song_chunk:
                im = self.generate_front(song['artist'], song['title'], song['year'], qr_id=song['token'], outline=True if ("BOTH" in outlines or "FRONT" in outlines) else False)
                images.append(im)

            pages.append(self.generate_page(images, False))

            images = []
            for song in song_chunk:
                im = self.generate_back(song['token'], show_qr_text=True, outline=True if ("BOTH" in outlines or "BACK" in outlines) else False)
                images.append(im)

            pages.append(self.generate_page(images, True))
        self.generate_pdf(pages, filename)
    

if __name__ == "__main__":
    import time
    print("Starting image generation...")
    start_time = time.time()
    cg = CardGenerator()

    test_data = [
        {"artist": "Lunara", "title": "Midnight Echoes", "year": 2017, "token": "a1b2c3d4"},
        {"artist": "Jake Orion", "title": "Neon Drive", "year": 2020, "token": "e5f6a7b8"},
        {"artist": "Zyra", "title": "Glass Garden", "year": 2015, "token": "9c8d7e6f"},
        {"artist": "Nico Blaze", "title": "Skyburn", "year": 2019, "token": "1234abcd"},
        {"artist": "Velin", "title": "Echo Tide", "year": 2016, "token": "deafbeef"},
        {"artist": "Aria Nocturne", "title": "Velvet Silence", "year": 2018, "token": "0badf00d"},
        {"artist": "Tovian", "title": "Binary Soul", "year": 2021, "token": "cafebabe"},
        {"artist": "Mira Sol", "title": "Crystal Veins", "year": 2014, "token": "deadbeef"},
        {"artist": "Kaze", "title": "Whirlwind Love", "year": 2022, "token": "beadface"},
        {"artist": "Leo Arc", "title": "Gravity Pulse", "year": 2023, "token": "f00dbabe"},
    ]

    test_data += [ # Extend to test with more than 10 songs
        {"artist": "Sena Voss", "title": "Moontrace", "year": 2013, "token": "ab12cd34"},
        {"artist": "Orion Flux", "title": "Nova Drift", "year": 2024, "token": "beefcafe"},
        {"artist": "Lyra", "title": "Silver Thread", "year": 2011, "token": "faceb00c"},
        {"artist": "Juno Ray", "title": "Echo Spiral", "year": 2020, "token": "c0ffee99"},
        {"artist": "Nahlia", "title": "Frozen Bloom", "year": 2017, "token": "feed1234"},
        {"artist": "Riven Skye", "title": "Shadow Orbit", "year": 2023, "token": "deadc0de"},
]
    cg.pdf_from_songs(test_data, "test_songs.pdf", "FRONT")


    print(f"Execution time: {time.time() - start_time:.2f} seconds")
