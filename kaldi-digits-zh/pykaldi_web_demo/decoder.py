from kaldi.asr import Recognizer
from kaldi.decoder import LatticeFasterDecoder, LatticeFasterDecoderOptions
from kaldi.feat.mfcc import Mfcc, MfccOptions
from kaldi.feat.functions import compute_deltas, DeltaFeaturesOptions
from kaldi.fstext import SymbolTable, read_fst_kaldi
from kaldi.gmm.am import AmDiagGmm, DecodableAmDiagGmmScaled
from kaldi.transform.cmvn import Cmvn
from kaldi.hmm import TransitionModel
from kaldi.util.io import xopen

# Define the feature pipeline: (wav) -> feats
def make_feat_pipeline(base, opts=DeltaFeaturesOptions(), cmvn= Cmvn(13)):
    def feat_pipeline(wav):
        feats = base.compute_features(wav.data()[0], wav.samp_freq, 1.0)
        cmvn.accumulate(feats)
        cmvn.apply(feats)
        return compute_deltas(opts, feats)
    return feat_pipeline

mfcc_opts = MfccOptions()
mfcc_opts.frame_opts.samp_freq = 44100
mfcc_opts.frame_opts.allow_downsample = True
mfcc_opts.use_energy = False

feat_pipeline = make_feat_pipeline(Mfcc(mfcc_opts))

# Read the model
with xopen("models/mono/final.mdl") as ki:
    trans_model = TransitionModel().read(ki.stream(), ki.binary)
    acoustic_model = AmDiagGmm().read(ki.stream(), ki.binary)

# Define the decodable wrapper: (features, acoustic_scale) -> decodable
def make_decodable_wrapper(trans_model, acoustic_model):
    def decodable_wrapper(features, acoustic_scale):
        return DecodableAmDiagGmmScaled(acoustic_model, trans_model,
                                        features, acoustic_scale)
    return decodable_wrapper

decodable_wrapper = make_decodable_wrapper(trans_model, acoustic_model)

# Define the decoder
decoding_graph = read_fst_kaldi("models/mono/graph/HCLG.fst")
decoder_opts = LatticeFasterDecoderOptions()
decoder_opts.beam = 13.0
decoder_opts.lattice_beam = 6.0
decoder = LatticeFasterDecoder(decoding_graph, decoder_opts)

# Define the recognizer
symbols = SymbolTable.read_text("models/mono/graph/words.txt")
asr = Recognizer(decoder, decodable_wrapper, symbols)

# Decode wave files
# for key, wav in SequentialWaveReader("scp:wav.scp"):
    # feats = feat_pipeline(wav)
    # out = asr.decode(feats)
    # print(key, out["text"], flush=True)
