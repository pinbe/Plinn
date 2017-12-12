(function() {
    window.addEventListener('load', function() {
        var fixedContent = document.getElementById('fixed-content');
        var options = JSON.parse(fixedContent.firstElementChild.getAttribute('data-options'));

        var stitchAtterElt = (options.stitch_after) ?
            document.querySelector(options.stitch_after) :
            null;
        var topOffset = (stitchAtterElt) ?
            function() {
                return Math.max(stitchAtterElt.getBoundingClientRect().bottom, 0) ;
            } :
            function() {
                return 0;
            };
        fixedContent.style.top = topOffset() + 'px';


        var speedup = (options.bg_scroll_speedup) ? parseFloat(options.bg_scroll_speedup) : 0.5;
        speedup = (isNaN(speedup)) ? 0.5 : speedup;

        window.addEventListener('scroll', function() {
            fixedContent.style.top = topOffset() - (window.scrollY * speedup) + 'px';
        });

    });
}());