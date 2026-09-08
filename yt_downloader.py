import os
import tempfile
import imageio_ffmpeg
import streamlit as st
from yt_dlp import YoutubeDL

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

st.title("Baixador de vídeos do Youtube (liste todos os vídeos por linha)")

arquivo_cookie = st.file_uploader("Arquivo cookies.txt")
video_txt_area = st.text_area("Link(s) do(s) vídeo(s)", height=200)
URLS = [url.strip() for url in video_txt_area.split("\n") if url.strip()]

formato_escolha = st.radio(
    "Escolha o formato:", ["MP4 (Vídeo Melhor Qualidade)", "MP3 (Apenas Áudio)"]
)
baixar_button = st.button("Processar Vídeo")

if baixar_button:
  if not arquivo_cookie:
    st.warning("Arquivo cookie necessário!")
  elif not URLS:
    st.warning("Insira pelo menos um link de vídeo.")
  else:
    # 1. Salva os cookies enviados temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
      tmp.write(arquivo_cookie.getvalue())
      caminho_cookie = tmp.name

    # 2. Pasta temporária isolada para receber a mídia
    pasta_download = tempfile.mkdtemp()
    template_saida = os.path.join(pasta_download, "%(title)s.%(ext)s")

    formatacao = {
        "outtmpl": template_saida,
        "cookiefile": caminho_cookie,
        "ffmpeg_location": FFMPEG_PATH,
        "js_runtimes": {"node": {}},
        "remote_components": ["ejs:github"],
        "nocheckcertificate": True,
        # Bula o bloqueio de IP de datacenter simulando cliente mobile
        "extractor_args": {
            "youtube": {
                "player_client": ["ios", "android", "mweb"],
            }
        },
    }

    if formato_escolha == "MP4 (Vídeo Melhor Qualidade)":
      formatacao["format"] = (
          "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
      )
      formatacao["merge_output_format"] = "mp4"
    else:
      formatacao["format"] = "bestaudio/best"
      formatacao["postprocessors"] = [{
          "key": "FFmpegExtractAudio",
          "preferredcodec": "mp3",
          "preferredquality": "192",
      }]

    try:
      with st.spinner("Processando vídeo no servidor..."):
        with YoutubeDL(formatacao) as ydl:
          ydl.download(URLS)

      arquivos_baixados = os.listdir(pasta_download)

      if arquivos_baixados:
        nome_arquivo = arquivos_baixados[0]
        caminho_arquivo = os.path.join(pasta_download, nome_arquivo)

        with open(caminho_arquivo, "rb") as f:
          st.success("Vídeo processado com sucesso!")
          st.download_button(
              label=f"⬇️ Baixar {nome_arquivo}",
              data=f,
              file_name=nome_arquivo,
              mime="video/mp4"
              if formato_escolha.startswith("MP4")
              else "audio/mpeg",
          )
      else:
        st.error("Não foi possível gerar o arquivo final.")

    except Exception as e:
      st.error(f"Ocorreu um erro durante o download: {e}")

    finally:
      if os.path.exists(caminho_cookie):
        os.remove(caminho_cookie)