document.addEventListener("DOMContentLoaded", () => {
    let lastScrollTop = 0;
    const navbar = document.querySelector(".navbar");
    const scrollTopBtn = document.getElementById("scrollTopBtn");
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.querySelector(".navbar-collapse");
    const scrollLimit = 150;
    const mobileLimit = 992;

    window.addEventListener("scroll", () => {
        let currentScroll = window.scrollY;
        const isScrollingDown = currentScroll > lastScrollTop && currentScroll > scrollLimit;
        const isNavOpen = document.body.classList.contains("nav-open");

        navbar.classList.toggle("fixed-top", !(isScrollingDown && !isNavOpen));
        scrollTopBtn.classList.toggle("fixed-bottom", currentScroll > scrollLimit && !isNavOpen);
        scrollTopBtn.classList.toggle("d-none", currentScroll < scrollLimit || isNavOpen);

        lastScrollTop = Math.max(0, currentScroll);
    });

    navbarToggler.addEventListener("click", () => {
        document.body.classList.toggle("nav-open");
        const isNavOpen = document.body.classList.contains("nav-open");
        scrollTopBtn.classList.toggle("d-none", isNavOpen || window.scrollY < scrollLimit);
    });

    document.querySelectorAll(".navbar-nav a").forEach(link => {
        link.addEventListener("click", () => {
            if (window.innerWidth < mobileLimit) {
                navbarCollapse.classList.remove("show");
                document.body.classList.remove("nav-open");
            }
        });
    });
});
