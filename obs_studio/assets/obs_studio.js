function open_scenes(){
    console.log("open_scenes")

    let scenes_url = "/obs/scenes";

    response =  fetch(scenes_url).then(response => response.json())
    .then(data => {
        console.log(data.data)
        updateGrid(data.data)

    })
}
