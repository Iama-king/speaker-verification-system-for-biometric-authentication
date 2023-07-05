from pydub import AudioSegment
import os
def audiosplit(audio , name ):
    start = 5000
    threshold = 35000 #4 secs
    end = 0
    counter = 0

    while start < len(audio):

        end += threshold

        chunk = audio[start:end] #audio chunk

        filename = f'D:/audio/splits2/{name}/{name}{counter}.wav'

        chunk.export(filename, format="wav")

        counter +=1

        start += threshold
data_directory = "D:/audio/cleaned"
parent_dir = "D:/audio/splits2"  # path where the splitting audio will present
i = 0
for k in os.listdir(data_directory):
    name = (k.split('.'))[0]

    path = os.path.join(parent_dir, name)

    if not os.path.isdir(path):
        os.mkdir(path)

    file_path = os.path.join(data_directory, k)
    audio = AudioSegment.from_file(file_path)
    audiosplit(audio, name)
