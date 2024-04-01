import os
import logging
import yt_dlp
from flask import Flask, render_template, request, send_file, url_for
from pathlib import Path

app = Flask(__name__, static_url_path='/static')

DOWNLOAD_FOLDER = os.path.join(Path.home(), "Downloads")


class VideoDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder

    def download_video(self, video_url):
        try:
            os.makedirs(self.download_folder, exist_ok=True)

            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(self.download_folder, '%(id)s_%(resolution)s.%(ext)s'),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                download_path = ydl.prepare_filename(info_dict)

                logging.info(f"Video downloaded at: {download_path}\n")
                return True, download_path

        except yt_dlp.DownloadError as e:
            logging.error(f"Error downloading video: {e}\n")
            return False, str(e)

        except Exception as e:
            logging.error(f"Unexpected error: {e}\n")
            return False, str(e)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form["video_url"]
        downloader = VideoDownloader(DOWNLOAD_FOLDER)
        success, message_or_path = downloader.download_video(video_url)
        if success:
            try:
                return send_file(message_or_path, as_attachment=True)
            finally:
                # Delete the downloaded file after sending
                os.remove(message_or_path)
        else:
            return render_template("index.html", message=message_or_path)
    return render_template("index.html", message=None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="download.log", filemode="a",
                        format="%(asctime)s - %(levelname)s - %(message)s")
    app.run(debug=False, host='0.0.0.0', port=8080)
