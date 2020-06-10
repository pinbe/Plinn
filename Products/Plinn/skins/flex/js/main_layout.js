(function() {
    var getWindowScrollY = (window.scrollY !== undefined) ?
        function() {
            return window.scrollY;
        } :
        function() {
            return document.documentElement.scrollTop;
        };

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

    function stretchLogo() {
        var logo = document.getElementById('portal-logo');
        var natHeight = logo.naturalHeight;
        var menu = document.getElementById('site-menu');
        var minTopbarheight = (menu) ?
            parseInt(window.getComputedStyle(menu).fontSize) :
            natHeight / 2;
        logo.height = Math.min(natHeight,
                               Math.max(natHeight - getWindowScrollY(),
                                        minTopbarheight));
        logo.width = logo.height * (logo.naturalWidth / natHeight);
    }

    window.addEventListener('load', function() {
        if(document.body.getAttribute('data-isAnon') === 'True') {
            fixTopBar();
            window.addEventListener('resize', fitTopBar);
            window.addEventListener('scroll', stretchLogo);
        }
    });

}());