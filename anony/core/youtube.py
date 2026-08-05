


import os
import re
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path

from py_yt import Playlist, VideosSearch

from anony import logger
from anony.helpers import Track, utils

# API Configuration
API_URL = os.environ.get("API_URL", "")
API_KEY = os.environ.get("API_KEY", "")

# Embedded Cookies Data (သင်ပေးပို့လိုက်သော Cookies များ)
EMBEDDED_COOKIES = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1771645301	LOGIN_INFO	AFmmF2swRQIhAPeUceY3QHqzUmr40ibIbZgxAb9C0zwq1ImKRaMISpNIAiBs69dacffXx_kY3qswguHzxtrEI0KSJhWQqJTAX6elXA:QUQ3MjNmd2ZpZFhPZy1SckY4VFRsZWVJNVlIMzFSNjgxdFRnN0xGODlrd0lwQzE3dDlpMHNVR29mdkoxalAzZW9NMXB2aER6Y1B5dUJXUFBIYTVrMUJpaHZvWXB3R3FYam81cnJzZ01sTm9jMVBjRXlBalVMSVlxWTIzZjFMQlJTbFk1YUl6cmhxejdUQ3JDUkZyb2t2cnhDaF9FY1hHZWFR
.youtube.com	TRUE	/	TRUE	1803706157	PREF	f4=4000000&tz=America.Guatemala&f7=100&f5=20000
.youtube.com	TRUE	/	FALSE	1803702813	HSID	AzEwUruLom4-XwkQu
.youtube.com	TRUE	/	TRUE	1803702813	SSID	AaNOtVEgH6u3hTf4d
.youtube.com	TRUE	/	FALSE	1803702813	APISID	_jD5F8_c3ottRvgT/Aa5VGOj4XKWf2LCCK
.youtube.com	TRUE	/	TRUE	1803702813	SAPISID	gl0kG0BYo2tyebpy/ApRzIVLeSUrR-K1ey
.youtube.com	TRUE	/	TRUE	1803702813	__Secure-1PAPISID	gl0kG0BYo2tyebpy/ApRzIVLeSUrR-K1ey
.youtube.com	TRUE	/	TRUE	1803702813	__Secure-3PAPISID	gl0kG0BYo2tyebpy/ApRzIVLeSUrR-K1ey
.youtube.com	TRUE	/	FALSE	1803702813	SID	g.a0006Ai2dHcEVFaNAiR6ztLa0zvVIoMXBIap0KeYzgDZYmtBuki6du3kTTZMAaC35pDqDg6S9wACgYKAc0SARcSFQHGX2Mib_wNmHUwm7igI6kgNUUKjxoVAUF8yKpSvCTlJ5W0ebCERn91LItz0076
.youtube.com	TRUE	/	TRUE	1803702813	__Secure-1PSID	g.a0006Ai2dHcEVFaNAiR6ztLa0zvVIoMXBIap0KeYzgDZYmtBuki6E_F_ZQsTPIwibfYawZU21QACgYKAdoSARcSFQHGX2MiX1ntOUefsMm8p5-weSszIBoVAUF8yKo5GBbitSFh-Ifhnrw33n3u0076
.youtube.com	TRUE	/	TRUE	1803702813	__Secure-3PSID	g.a0006Ai2dHcEVFaNAiR6ztLa0zvVIoMXBIap0KeYzgDZYmtBuki6Skiv6cFhVJxy1TZLLK2Q6AACgYKAbYSARcSFQHGX2MiC26Zfvg_y2-pyArWKMdOLRoVAUF8yKpn4Ekm94ZWwDvlxez8iuHT0076
.youtube.com	TRUE	/	TRUE	1800682167	__Secure-1PSIDTS	sidts-CjQB7I_69KExocpfh8AoXfbzwmrbIK5wyTo_4sQ8BahjOEDVpt1hfKUhHekuL1wpL5XZJlUYEAA
.youtube.com	TRUE	/	TRUE	1800682167	__Secure-3PSIDTS	sidts-CjQB7I_69KExocpfh8AoXfbzwmrbIK5wyTo_4sQ8BahjOEDVpt1hfKUhHekuL1wpL5XZJlUYEAA
.youtube.com	TRUE	/	FALSE	1800682170	SIDCC	AKEyXzUeAdH-92qHBG2XQoQlNfQ4IG9aVN0nGYw6p28tKEQSIZxSV2U5TH2F_lRC7Z-LvRkfpA
.youtube.com	TRUE	/	TRUE	1800682170	__Secure-1PSIDCC	AKEyXzU-apGpVVdOJDBAhcc11LGFm-vA_792uw1_WkxczQKCg40mSUY88r7Qcesii472nolYym4
.youtube.com	TRUE	/	TRUE	1800682170	__Secure-3PSIDCC	AKEyXzXGD5AVknQ6gY3Ycjt_U4rLGgjcOInYlMVCcI-8tvKHhzHMoLn-1hbDpX02yDelavQZhQ
.youtube.com	TRUE	/	TRUE	1784698151	VISITOR_INFO1_LIVE	VkCJsATDS9M
.youtube.com	TRUE	/	TRUE	1784698151	VISITOR_PRIVACY_METADATA	CgJNTRIEGgAgHw%3D%3D
.youtube.com	TRUE	/	TRUE	1784694813	__Secure-ROLLOUT_TOKEN	CJ3jx7ncs_iGrwEQ6_bNiev7igMY0-_Rx-qgkgM%3D
.youtube.com	TRUE	/	TRUE	0	YSC	NJSFiW2pzmY
"""

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.cookie_dir = "anony/cookies"
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        self.iregex = re.compile(
            r"https?://(?:www\.|m\.|music\.)?(?:youtube\.com|youtu\.be)"
            r"(?!/(watch\?v=[A-Za-z0-9_-]{11}|shorts/[A-Za-z0-9_-]{11}"
            r"|playlist\?list=PL[A-Za-z0-9_-]+|[A-Za-z0-9_-]{11}))\S*"
        )
        
        # Cookies မရှိသေးပါက တခါတည်း စာကြောင်းအတိုင်း auto ဖန်တီးပေးမည်
        self._ensure_embedded_cookies()

    def _ensure_embedded_cookies(self):
        """အကယ်၍ cookie ဖိုင်များ မရှိပါက ပေးထားသော Cookies များကို auto ရေးသွင်းမည်"""
        try:
            os.makedirs(self.cookie_dir, exist_ok=True)
            default_cookie_file = os.path.join(self.cookie_dir, "youtube.txt")
            
            # ဖိုင်မရှိသေးလျှင် (သို့) ဖိုင်အလွတ်ဖြစ်နေလျှင် ရေးထည့်မည်
            if not os.path.exists(default_cookie_file) or os.path.getsize(default_cookie_file) == 0:
                with open(default_cookie_file, "w", encoding="utf-8") as f:
                    f.write(EMBEDDED_COOKIES.strip())
                logger.info("Embedded YouTube cookies saved successfully.")
        except Exception as e:
            logger.error(f"Failed to write embedded cookies: {e}")

    def get_cookies(self):
        if not self.checked:
            if os.path.exists(self.cookie_dir):
                for file in os.listdir(self.cookie_dir):
                    if file.endswith(".txt"):
                        self.cookies.append(f"{self.cookie_dir}/{file}")
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        return random.choice(self.cookies)

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        os.makedirs(self.cookie_dir, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            for url in urls:
                name = url.split("/")[-1]
                link = "https://batbin.me/raw/" + name
                async with session.get(link) as resp:
                    resp.raise_for_status()
                    with open(f"{self.cookie_dir}/{name}.txt", "wb") as fw:
                        fw.write(await resp.read())
        logger.info(f"Cookies saved in {self.cookie_dir}.")

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def invalid(self, url: str) -> bool:
        return bool(re.match(self.iregex, url))

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        try:
            _search = VideosSearch(query, limit=1, with_live=False)
            results = await _search.next()
        except Exception:
            return None
        if results and results["result"]:
            data = results["result"][0]
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track | None]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except Exception:
            pass
        return tracks

    async def download(self, video_id: str, video: bool = False) -> str | None:
        url = self.base + video_id
        ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{ext}"

        if Path(filename).exists() and Path(filename).stat().st_size > 0:
            return filename

        os.makedirs("downloads", exist_ok=True)
        api_type = "video" if video else "audio"

        # --- 1. ပထမဦးဆုံး ShrutiBots API ဖြင့် Download ဆွဲရန် ကြိုးစားမည် ---
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_URL}/download",
                    params={"url": video_id, "type": api_type, "api_key": API_KEY},
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as resp:
                    if resp.status == 200:
                        with open(filename, "wb") as f:
                            async for chunk in resp.content.iter_chunked(131072):
                                f.write(chunk)
                        if Path(filename).exists() and Path(filename).stat().st_size > 0:
                            return filename
        except Exception as e:
            logger.warning(f"ShrutiBots API failed, falling back to yt-dlp: {e}")

        # အကယ်၍ API ကျသွားလျှင် (သို့) Error တက်လျှင် ဖိုင်အကျိုးအပဲ့များကို ဖယ်ရှားမည်
        if Path(filename).exists():
            try:
                os.remove(filename)
            except Exception:
                pass

        # --- 2. API မအောင်မြင်ပါက yt_dlp ဖြင့် Cookies အသုံးပြု၍ Download ဆွဲမည် ---
        cookie = self.get_cookies()
        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "nocheckcertificate": True,
            "cookiefile": cookie,
        }

        if video:
            ydl_opts = {
                **base_opts,
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio)",
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[ext=webm][acodec=opus]",
            }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                except (yt_dlp.utils.DownloadError, yt_dlp.utils.ExtractorError) as e:
                    logger.error(f"yt-dlp DownloadError: {e}")
                    return None
                except Exception as ex:
                    logger.warning("Download failed: %s", ex)
                    return None
            return filename

        result_file = await asyncio.to_thread(_download)
        if result_file and Path(result_file).exists() and Path(result_file).stat().st_size > 0:
            return result_file
        return None
