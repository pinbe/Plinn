(function() {
    window.addEventListener('load', function() {
        var fixedContent = document.getElementById('fixed-content');
        var options = JSON.parse(fixedContent.firstElementChild.getAttribute('data-options'));
        console.log(options);

        var stitchAtterElt = (options.stitch_after) ?
            document.querySelector(options.stitch_after) :
            null;
        var topOffset = (stitchAtterElt) ?
            function() {
                return stitchAtterElt.getBoundingClientRect().bottom;
            } :
            function() {
                return 0;
            };
        fixedContent.style.top = topOffset() + 'px';


        var speedup = (options.bg_scroll_speedup) ? parseInt(options.bg_scroll_speedup) : 0.5;
        speedup = (speedup === NaN) ? 0.5 : speedup;

        window.addEventListener('scroll', function() {
            fixedContent.style.top = topOffset() - (window.scrollY * speedup) + 'px';
        });

    });
}());