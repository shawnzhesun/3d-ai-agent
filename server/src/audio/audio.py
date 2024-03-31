import json
from pydub import AudioSegment
from pydub.silence import split_on_silence
import whisper
from openai import OpenAI

def generate_mouth_cues(audio, threshold=-60, min_silence_len=100, chunk_length=150):
    """
    Generate mouth cues based on sound and silence.
    Parameters:
    - audio: Loaded audio segment.
    - threshold: Silence threshold in dB.
    - min_silence_len: Minimum length of a silence to consider in milliseconds.
    - chunk_length: Duration of each audio chunk analyzed for mouth shape alternation in milliseconds.
    Returns a list of mouth cues.
    """
    # Split audio based on silence
    chunks = split_on_silence(audio, silence_thresh=threshold, min_silence_len=min_silence_len, keep_silence=300)

    cues = []
    start_time = 0.0
    mouth_shapes = ["A", "B", "C", "D", "E", "F", "G", "H"]
    mouth_index = 0

    for chunk in chunks:
        # Calculate chunk duration
        chunk_duration = len(chunk) / 1000.0

        print(chunk_duration)

        # Split chunk into smaller pieces
        num_pieces = max(1, int(chunk_duration * 1000 / chunk_length))
        piece_duration = chunk_duration / num_pieces

        for i in range(num_pieces):
            end_time = start_time + piece_duration
            cue = {
                "start": round(start_time, 2),
                "end": round(end_time, 2),
                "value": mouth_shapes[mouth_index]
            }
            cues.append(cue)
            start_time = end_time
            mouth_index = (mouth_index + 1) % len(mouth_shapes)

        # Assume a short silence after each chunk before the next chunk (or end)
        if start_time < len(audio) / 1000.0:
            end_time = start_time + 0.1 # 0.1 second of silence
            cue = {
                "start": round(start_time, 2),
                "end": round(end_time, 2),
                "value": "X" # Closed mouth for silence
            }
            cues.append(cue)
            start_time = end_time

    return cues

def generate_json_from_mp3(mp3_path):
    audio = AudioSegment.from_mp3(mp3_path)
    duration_seconds = len(audio) / 1000.0
    mouth_cues = generate_mouth_cues(audio)

    data = {
        "metadata": {
            "soundFile": mp3_path,
            "duration": duration_seconds
        },
        "mouthCues": mouth_cues
    }
    print(json.dumps(data))


def speech_to_text(mp3_path: str) -> str:
    model = whisper.load_model("small.en")
    result = model.transcribe(mp3_path, fp16=False)
    return(result["text"])

def text_to_speech(text: str, file_path: str) -> None:
    client = OpenAI()
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    response.write_to_file(file_path)

