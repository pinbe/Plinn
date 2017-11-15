(function() {
    window.addEventListener('load', function() {
        var fixedContent = document.getElementById('fixed-content');
        window.addEventListener('scroll', function(evt) {
            fixedContent.style.top = - (evt.pageY/2) + 'px';
        });

    });
}());