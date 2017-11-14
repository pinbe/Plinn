(function() {
    function fixTopBar() {
        var topBar = document.getElementById('top-bar');
        var topBarRect = topBar.getBoundingClientRect();
        topBar.style.position = 'fixed';
        document.getElementById('content-outer').style.paddingTop = topBarRect.height + 'px';
        fitTopBar();
    }

    function fitTopBar() {
        var topBar = document.getElementById('top-bar');
        var content = document.getElementById('content-outer');
        var contentCStyle = getComputedStyle(content);
        topBar.style.width =
            content.getBoundingClientRect().width +
            parseInt(contentCStyle.marginLeft) +
            parseInt(contentCStyle.marginRight) +
            'px';
    }

    window.addEventListener('load', function() {
        if(document.body.getAttribute('data-isAnon') === 'True') {
            fixTopBar();
            window.addEventListener('resize', fitTopBar);
        }
    });
}());