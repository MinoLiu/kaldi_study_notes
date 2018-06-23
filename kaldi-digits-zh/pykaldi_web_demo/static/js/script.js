'use strict'

let log = console.log.bind(console),
    id = val => document.getElementById(val),
    ul = id('ul'),
    gUMbtn = id('gUMbtn'),
    start = id('start'),
    stop = id('stop'),
    remove = id('remove'),
    stream,
    recorder,
    counter=1,
    media;


let mediaOptions = {
    video: {
        tag: 'video',
        type: 'video/webm',
        ext: '.mp4',
        gUM: {video: true, audio: true}
    },
    audio: {
        tag: 'audio',
        type: 'audio/wav',
        ext: '.wav',
        gUM: {audio: true}
    }
};

media = mediaOptions.audio
navigator.mediaDevices.getUserMedia(media.gUM).then(_stream => {
    stream = _stream;
    id('btns').style.display = 'block';
    start.removeAttribute('disabled');
    recorder = new MediaStreamRecorder(stream);
    recorder.mimeType = media.type;
    recorder.audioChannels = 1;
    recorder.ondataavailable = blob => {
        makeLink(blob)
    };
    log('got media successfully');
}).catch(log);

start.onclick = e => {
    start.disabled = true;
    stop.removeAttribute('disabled');
    recorder.start(10000);
}


stop.onclick = e => {
    stop.disabled = true;
    recorder.stop();
    start.removeAttribute('disabled');
}


function removeLi(){
    [ ...ul.children].map( c => {
        ul.removeChild(c);
    });
};

remove.onclick = e => {
    removeLi();
}

function makeLink(blob){
    let url = URL.createObjectURL(blob)
        , li = document.createElement('li')
        , mt = document.createElement(media.tag)
        , hf = document.createElement('a')
    ;
    mt.controls = true;
    mt.src = url;
    hf.href = url;
    hf.download = `${counter++}${media.ext}`;
    hf.innerHTML = `donwload ${hf.download}`;
    li.appendChild(mt);
    li.appendChild(hf);
    ul.appendChild(li);
    var fd = new FormData();
    fd.append("file", blob, "decode.wav")
    fetch('upload_wav',
        {
            method: 'post',
            body: fd
        }
    ).then(res => res.json())
        .catch(error => console.error('Error:', error))
        .then(response => {
            let result = document.createElement('p');
            result.innerHTML = response.text;
            li.appendChild(result);
        })
}

