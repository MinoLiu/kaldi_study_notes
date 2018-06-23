from sanic import Sanic, response
from io import BytesIO
from decoder import feat_pipeline, asr
from kaldi.matrix import Vector
from scipy.io.wavfile import read

app = Sanic(__name__)

app.static('/static', './static')

# for feat_pipeline
class Wave:
    def __init__(self, freq, vector):
        self.samp_freq = freq
        self.vector = vector

    def data(self):
        return [Vector(self.vector)]

@app.route('/')
async def index(request):
    return await response.file('index.html')

@app.route('/upload_wav', methods=['POST'])
def upload_wav(request):
    fd = request.files.get('file',None)
    if fd:
        b = BytesIO(fd.body)
        rate, vector = read(b)
        wav = Wave(rate , vector)
        feat = feat_pipeline(wav)
        out = asr.decode(feat)
        if not out['text']:
            text = 'None'
        else:
            text = out['text']
        return response.json({'text': text })
    else:
        return response.json({'text': 'error'})

if __name__ == '__main__':
    app.run("0.0.0.0", port=8000, debug=True, workers=4)
