document.addEventListener('DOMContentLoaded', () => {
    const megaDropdown = document.querySelector('.courses-mega-dropdown');

    if (!megaDropdown) {
        return;
    }

    const toggle = megaDropdown.querySelector('.dropdown-toggle');
    const menu = megaDropdown.querySelector('.mega-menu');

    if (!toggle || !menu) {
        return;
    }

    const isDesktop = () => window.innerWidth >= 1200;

    const openMenu = () => {
        if (!isDesktop()) {
            return;
        }

        megaDropdown.classList.add('show');
        toggle.setAttribute('aria-expanded', 'true');
    };

    const closeMenu = () => {
        if (!isDesktop()) {
            return;
        }

        megaDropdown.classList.remove('show');
        toggle.setAttribute('aria-expanded', 'false');
    };

    megaDropdown.addEventListener('mouseenter', openMenu);
    megaDropdown.addEventListener('mouseleave', closeMenu);

    toggle.addEventListener('click', (event) => {
        if (isDesktop()) {
            event.preventDefault();
            if (megaDropdown.classList.contains('show')) {
                closeMenu();
            } else {
                openMenu();
            }
        }
    });

    window.addEventListener('resize', () => {
        if (!isDesktop()) {
            closeMenu();
        }
    });
});
