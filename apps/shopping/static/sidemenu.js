$(document).ready(function () {
    // Event handler for clicks on outer li elements
    $(".sidebar ul li.menu-collapse-label").on('click', function () {
        if (!$(this).hasClass('active')) {
            $(".sidebar ul li.menu-collapse-label.active").removeClass('active');
            $(this).addClass('active');
            $(".sidebar ul li.menu-collapse-label .collapse.show").collapse('hide');
        }
    });

    // Event handler for clicks on inner ul and li elements
    $(".sidebar ul li.menu-collapse-label ul, .sidebar ul li.menu-collapse-label li").on('click', function (event) {
        event.stopPropagation();
    });
});
