function open_soundboard(soundboard_id){

    let soundboard_url = "/voicemod/generate_soundboard/"+ soundboard_id;

    response =  fetch(soundboard_url).then(response => response.json())
    .then(data => {
        console.log(data.data)
        updateGrid(data.data)

    })
    
}

function open_voices(){
    let voices_url = "/voicemod/generate_voices";
    response =  fetch(voices_url).then(response => response.json())
    .then(data => {
        
        updateGrid(data.data)
        })
}