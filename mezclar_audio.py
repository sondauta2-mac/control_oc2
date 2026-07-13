from moviepy import VideoFileClip, AudioFileClip

try:
    print("🎬 Cargando archivos con MoviePy 2.x...")
    # 1. Cargamos el video que grabaste de la pantalla
    video = VideoFileClip("video_limpio.mp4")
    
    # 2. Cargamos la música de fondo
    musica = AudioFileClip("musica.mp3")
    
    # 3. CORRECCIÓN: Usamos .subclipped() en lugar de .subclip()
    # Ajusta la música para que dure lo mismo que el video y baja el volumen al 15% (0.15)
    musica_ajustada = musica.subclipped(0, video.duration).with_volume_scaled(0.15)
    
    print("🎵 Mezclando video y audio de fondo...")
    # 4. Inyectamos la música de fondo al video
    video_final = video.with_audio(musica_ajustada)
    
    print("💾 Guardando el video final (esto puede tardar unos segundos)...")
    # 5. Exportamos el archivo de video final definitivo
    video_final.write_videofile("presentacion_final.mp4", codec="libx264", audio_codec="aac")
    
    # Cerramos los archivos para liberar la memoria de la PC
    video.close()
    musica.close()
    video_final.close()
    print("✅ ¡Éxito total! Se ha creado 'presentacion_final.mp4' con la música de fondo perfecta.")

except Exception as e:
    print(f"❌ Ocurrió un error: {e}")
