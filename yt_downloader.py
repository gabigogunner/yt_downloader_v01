import os
import shutil
import subprocess
import tempfile
import traceback
import zipfile

import imageio_ffmpeg
import streamlit as st
from yt_dlp import YoutubeDL

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


def node_disponivel():
    """Confere se o Node.js está instalado e acessível no PATH.
    Evita quebrar em ambientes (ex: rodando local) onde o package.txt
    (usado só pelo Streamlit Cloud) não foi aplicado."""
    return shutil.which("node") is not None


st.title("Baixador de vídeos do YouTube")

arquivo_cookie = st.file_uploader(
    "Arquivo cookies.txt (Opcional - Apenas se o vídeo exigir login)"
)
video_txt_area = st.text_area("Link(s) do(s) vídeo(s)", height=150)
URLS = [url.strip() for url in video_txt_area.split("\n") if url.strip()]

formato_escolha = st.radio(
    "Escolha o formato:", ["MP4 (Vídeo Melhor Qualidade)", "MP3 (Apenas Áudio)"]
)
baixar_button = st.button("Processar Vídeo")

# Extensões que NÃO devem ser consideradas "arquivo final" na pasta de download
EXTENSOES_IGNORAR = (".part", ".ytdl", ".json", ".description", ".webp", ".jpg", ".png")


def listar_arquivos_finais(pasta):
    return sorted(
        f for f in os.listdir(pasta)
        if not f.endswith(EXTENSOES_IGNORAR)
    )


if baixar_button:
    if not URLS:
        st.warning("Insira pelo menos um link de vídeo.")
    else:
        caminho_cookie = None

        # Processa o arquivo de cookie apenas se o usuário enviou um novo
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
            "ignoreerrors": True,  # não trava tudo se 1 de N links falhar
            "no_warnings": False,
            # Node.js disponível via package.txt -> deixa o yt-dlp resolver
            # desafios JS (ex: PO token) quando necessário
            "js_runtimes": {"node": {}},
            # Vários clients de fallback: se um for bloqueado/exigir JS, tenta o próximo
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web", "tv", "web_embedded"],
                }
            },
            # Usa curl-cffi (já está no requirements.txt) pra imitar o fingerprint
            # TLS de um navegador real -> reduz bloqueios/erros 403 do YouTube
            "impersonate": "chrome",
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
            with st.spinner("Processando vídeo(s) no servidor..."):
                with YoutubeDL(formatacao) as ydl:
                    ydl.download(URLS)

            arquivos_baixados = listar_arquivos_finais(pasta_download)

            if not arquivos_baixados:
                st.error(
                    "Não foi possível gerar o arquivo final. "
                    "Verifique se o link é válido, se o vídeo não é privado/idade-restrita "
                    "sem cookies, ou tente novamente (o YouTube às vezes bloqueia "
                    "temporariamente o servidor)."
                )
            elif len(arquivos_baixados) == 1:
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
                # Mais de um vídeo baixado -> zipa tudo para entregar num único arquivo
                zip_path = os.path.join(pasta_download, "videos.zip")
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for nome_arquivo in arquivos_baixados:
                        zipf.write(
                            os.path.join(pasta_download, nome_arquivo),
                            arcname=nome_arquivo,
                        )
                with open(zip_path, "rb") as f:
                    st.success(f"{len(arquivos_baixados)} vídeos processados com sucesso!")
                    st.download_button(
                        label="⬇️ Baixar todos (.zip)",
                        data=f,
                        file_name="videos.zip",
                        mime="application/zip",
                    )

        except Exception as e:
            st.error(f"Ocorreu um erro durante o download: {e}")
            with st.expander("Detalhes técnicos do erro"):
                st.code(traceback.format_exc())

        finally:
            if caminho_cookie and os.path.exists(caminho_cookie):
                os.remove(caminho_cookie)
            shutil.rmtree(pasta_download, ignore_errors=True)