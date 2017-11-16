(function() {
    window.addEventListener('load', function() {
        var fixedContent = document.getElementById('fixed-content');
        window.addEventListener('scroll', function() {
            fixedContent.style.top = - (window.scrollY / 2) + 'px';
        });

    });
}());