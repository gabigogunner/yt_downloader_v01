import os
import tempfile
import imageio_ffmpeg
import streamlit as st
from yt_dlp import YoutubeDL

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

st.title("Baixador de vídeos do Youtube")

arquivo_cookie = st.file_uploader("Arquivo cookies.txt (Opcional/Recomendado para restrições)")
video_txt_area = st.text_area("Link(s) do(s) vídeo(s)", height=150)
URLS = [url.strip() for url in video_txt_area.split("\n") if url.strip()]

formato_escolha = st.radio(
    "Escolha o formato:", ["MP4 (Vídeo Melhor Qualidade)", "MP3 (Apenas Áudio)"]
)
baixar_button = st.button("Processar Vídeo")

if baixar_button:
  if not URLS:
    st.warning("Insira pelo menos um link de vídeo.")
  else:
    caminho_cookie = None

    # Save cookie if uploaded
    if arquivo_cookie:
      with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(arquivo_cookie.getvalue())
        caminho_cookie = tmp.name

    pasta_download = tempfile.mkdtemp()
    template_saida = os.path.join(pasta_download, "%(title)s.%(ext)s")

    formatacao = {
        "outtmpl": template_saida,
        "ffmpeg_location": FFMPEG_PATH,
        "nocheckcertificate": True,
        "force_ipv4": True,
        # Personifica o navegador Chrome usando curl-cffi
        "impersonate": "chrome",
        # Altera os clientes para evitar o 403 nos servidores do googlevideo
        "extractor_args": {
            "youtube": {
                "player_client": ["mweb", "web", "tv"],
            }
        },
    }

    if caminho_cookie:
      formatacao["cookiefile"] = caminho_cookie

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
      if caminho_cookie and os.path.exists(caminho_cookie):
        os.remove(caminho_cookie)