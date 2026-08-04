# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic


import os
import base64
import aiohttp
from PIL import (Image, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont, ImageOps)

from anony import config
from anony.helpers import Track


class Thumbnail:
    def __init__(self):
        self.rect = (914, 514)
        self.fill = (255, 255, 255)
        self.mask = Image.new("L", self.rect, 0)
        self.font1 = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 30)
        self.font2 = ImageFont.truetype("anony/helpers/Inter-Light.ttf", 30)
        
        try:
            self.font_source = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 24)
            # အပေါ်ပိုင်းတွင် မြန်မာစာသားများ (သို့) အခြားစာသားများလှလှပပပေါ်ရန် Font ထည့်သွင်းခြင်း (မရှိပါက font1 ကိုသုံးမည်)
            self.font_top = ImageFont.truetype("anony/helpers/Raleway-Bold.ttf", 28)
        except Exception:
            self.font_source = self.font1
            self.font_top = self.font1

        self.session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        await self.session.close()

    async def save_thumb(self, output_path: str, url: str) -> str:
        async with self.session.get(url) as resp:
            with open(output_path, "wb") as f: 
                f.write(await resp.read())
        return output_path

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}.png"
            if os.path.exists(output):
                return output

            await self.save_thumb(temp, song.thumbnail)
            thumb = Image.open(temp).convert("RGBA").resize(
                size, Image.Resampling.LANCZOS,
            )
            blur = thumb.filter(ImageFilter.GaussianBlur(25))
            image = ImageEnhance.Brightness(blur).enhance(.40)

            _rect = ImageOps.fit(
                thumb, self.rect,
                method=Image.LANCZOS, centering=(0.5, 0.5),
            )
            ImageDraw.Draw(self.mask).rounded_rectangle(
                (0, 0, self.rect[0], self.rect[1]),
                radius=15,
                fill=255,
            )
            _rect.putalpha(self.mask)
            image.paste(_rect, (183, 30), _rect)

            draw = ImageDraw.Draw(image)
            
            # --- အပေါ်ပိုင်းတွင် ပုံစံတူ စာသားများ ပေါ်လာစေရန် (ဥပမာ - သီချင်းခေါင်း سر သို့မဟုတ် လှပသော စာသားများ) ---
            top_text_1 = ""
            top_text_2 = ""
            
            # ညာဘက်သို့ အနည်းငယ်ကပ်၍ အပေါ်ပိုင်းတွင် စာသားများ ရေးဆွဲခြင်း
            draw.text((750, 60), top_text_1, font=self.font_top, fill=self.fill)
            draw.text((850, 105), top_text_2, font=self.font_top, fill=self.fill)

            # ပုံမှန် အောက်ခြေ အချက်အလက်များ
            draw.text(
                xy=(50, 560),
                text=f"{song.channel_name[:25]} | {song.view_count}",
                font=self.font2, fill=self.fill,
            )
            draw.text((50, 600), song.title[:50], font=self.font1, fill=self.fill)
            draw.text((40, 650), "0:01", font=self.font1)
            draw.line([(140, 670), (1160, 670)], fill=self.fill, width=5, joint="curve")
            draw.text((1185, 650), song.duration, font=self.font1, fill=self.fill)

            # ---
            encoded_str = "U09VUkNFIC0gQEhBTlRIQVI5OTkgQENPUkVTXzk5OQ=="
            decoded_text = base64.b64decode(encoded_str).decode("utf-8")

            bbox = draw.textbbox((0, 0), decoded_text, font=self.font_source)
            text_width = bbox[2] - bbox[0]
            x_pos = (size[0] - text_width) / 2
            y_pos = 680  # 

            # ပုံမှာပြထားသည့်အတိုင်း တောက်ပြောင်သော ပန်းရောင် (Pink/Magenta) ဖြင့် ရေးဆွဲခြင်း
            draw.text((x_pos, y_pos), decoded_text, font=self.font_source, fill=(255, 105, 180))

            image.save(output)
            try: 
                os.remove(temp)
            except Exception: 
                pass
            return output
        except Exception:
            return config.DEFAULT_THUMB
