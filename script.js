async function loadPage(basepath,page){
    const container = document.getElementById('pageToLoad');
    const baseContainer = document.getElementById('basePagerContainer');
    baseContainer.href = "";
    if (container) {
        const response = await fetch(basepath+page);
        container.innerHTML = await response.text();;
    }
    baseContainer.href = basepath;
}

document.addEventListener('DOMContentLoaded',() => {loadPage("./pages/","aboutMe.html")})