function initPagination(pageLink){
    /* Get current page index if exits */
    window.sessionStorage.clear();
    const page = new URLSearchParams(window.location.search).get('page');
    if(page){
        window.sessionStorage.setItem('page', page);
    } else {
        window.sessionStorage.setItem('page', 1);
    }
    var currentPage = window.sessionStorage.getItem('page');

    /* Check Previous/Next button state */
    if (parseInt(currentPage) === 1){
        $('#prevItem').addClass("disabled");
    }
    if (parseInt(currentPage) === parseInt($('#pageAmount').val())){
        $('#nextItem').addClass("disabled");
    }

    /* Set current page index */
    $(`#pageItem${currentPage}`).addClass('active');

    /* Previous page */
    $('[id=prevPage]').on('click', function () {
        setSessionStorage('page', --currentPage);
        document.location.href = `${pageLink}?page=${currentPage}`;
    });

    /* Next page */
    $('[id=nextPage]').on('click', function () {
        setSessionStorage('page', ++currentPage);
        document.location.href = `${pageLink}?page=${currentPage}`;
    });

    /* Change storage value */
    function setSessionStorage(name, value) {
        window.sessionStorage.setItem(name, value);
    };
}