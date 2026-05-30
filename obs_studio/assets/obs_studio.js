function open_scenes(){
    console.log("open_scenes")

    let scenes_url = "/obs/scenes";

    response =  fetch(scenes_url).then(response => response.json())
    .then(data => {
        console.log(data.data)
        updateGrid(data.data)

    })
}

function open_sources(){
    console.log("open_sources")

    let sources_url = "/obs/sources";

    fetch(sources_url).then(response => response.json())
    .then(data => {
        console.log(data.data)
        updateGrid(data.data)
    })
}