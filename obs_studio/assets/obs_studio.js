function open_scenes(){
    console.log("open_scenes")

    let soundboard_url = "/obs/scenes";

    response =  fetch(soundboard_url).then(response => response.json())
    .then(data => {
        console.log(data.data)
        updateGrid(data.data)

    })
}
