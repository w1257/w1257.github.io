async function loadPage(page){
    const container = document.getElementById('pageToLoad');
    if (container) {
        const response = await fetch(page);
        container.innerHTML = await response.text();;
    }
}

document.addEventListener('DOMContentLoaded',() => {loadPage("./aboutMe.html")})