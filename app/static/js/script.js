document.addEventListener("DOMContentLoaded", () => {
    let lastScrollTop = 0;
    const navbar = document.querySelector(".navbar");
    const scrollTopBtn = document.getElementById("scrollTopBtn");
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.querySelector(".navbar-collapse");

    window.addEventListener("scroll", () => {
        let currentScroll = window.scrollY;
        const isScrollingDown = currentScroll > lastScrollTop && currentScroll > 150;
        const isNavOpen = document.body.classList.contains("nav-open");

        navbar.classList.toggle("fixed-top", !(isScrollingDown && !isNavOpen));
        scrollTopBtn.classList.toggle("fixed-bottom", currentScroll > 200 && !isNavOpen);

        lastScrollTop = Math.max(0, currentScroll);
    });

    navbarToggler.addEventListener("click", () => 
        document.body.classList.toggle("nav-open")
    );

    document.querySelectorAll(".navbar-nav a").forEach(link => {
        link.addEventListener("click", () => {
            if (window.innerWidth < 992) {
                navbarCollapse.classList.remove("show");
                document.body.classList.remove("nav-open");
            }
        });
    });
});
