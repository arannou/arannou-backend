
const BASE_URL = "http://127.0.0.1:5000"
const PROD_BASE_URL = "https://arannou-backend.onrender.com"

const HEADERS = {
    "Content-Type": "application/json",
    "accept": "application/json",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}

async function get_all_objects(object_type) {
    response = await fetch(BASE_URL+"/api/"+object_type, {
        "headers": HEADERS,
        "referrerPolicy": "strict-origin-when-cross-origin",
        "method": "GET",
        "mode": "cors"
    })
    if (!response.ok) {
        handleError(response)
    }
    return response.json()
}

async function create_object(object_type, new_object) {
    response = await fetch(BASE_URL+"/api/"+object_type, {
        "headers": HEADERS,
        "referrerPolicy": "strict-origin-when-cross-origin",
        "method": "POST",
        "body": JSON.stringify(new_object),
        "mode": "cors"
    })
    if (!response.ok) {
        handleError(response)
    }
    return response.json()
}

async function update_object(object_type, object_id, new_object) {
    response = await fetch(BASE_URL+"/api/"+object_type+"/"+object_id, {
        "headers": HEADERS,
        "referrerPolicy": "strict-origin-when-cross-origin",
        "method": "PUT",
        "body": JSON.stringify(new_object),
        "mode": "cors"
    })
    if (!response.ok) {
        handleError(response)
    }
    return response.json()
}

async function delete_object(object_type, object_name) {
    response = await fetch(BASE_URL+"/api/"+object_type+"/"+object_name, {
        "headers": HEADERS,
        "referrerPolicy": "strict-origin-when-cross-origin",
        "method": "DELETE",
        "mode": "cors"
    })
    if (!response.ok) {
        handleError(response)
    }
    return response.json()
}
function handleError(error) {
    error.json().then(e => {
        throw new Error(error.status + " "+ error.statusText + " \n" +JSON.stringify(e))
    })
}

