// SFAI SDK Documentation JavaScript Enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all enhancements
    initializeScrollProgress();
    initializeBackToTop();
    initializeCodeCopyButtons();
    initializeNotebookEnhancements();
    initializeSearchEnhancements();
    initializeAnimations();
    initializeTabTransitions();
});

// Enhanced tab transitions
function initializeTabTransitions() {
    const tabs = document.querySelectorAll('.md-tabs__link');
    const content = document.querySelector('.md-content__inner');

    tabs.forEach(function(tab) {
        tab.addEventListener('click', function(e) {
            // Add loading state
            if (content) {
                content.style.opacity = '0';
                content.style.transform = 'translateY(20px)';

                // Reset animation after short delay
                setTimeout(function() {
                    content.style.opacity = '1';
                    content.style.transform = 'translateY(0)';
                    content.style.animation = 'slideUpFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                }, 100);
            }

            // Add ripple effect to tab
            createRippleEffect(tab, e);
        });
    });

    // Also handle navigation links
    const navLinks = document.querySelectorAll('.md-nav__link');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (content && !link.getAttribute('href').startsWith('#')) {
                content.style.opacity = '0';
                content.style.transform = 'translateY(20px)';

                setTimeout(function() {
                    content.style.opacity = '1';
                    content.style.transform = 'translateY(0)';
                    content.style.animation = 'slideUpFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                }, 100);
            }
        });
    });
}

// Create ripple effect for tabs
function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s ease-out;
        pointer-events: none;
        z-index: 1;
    `;

    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);

    // Remove ripple after animation
    setTimeout(function() {
        if (ripple.parentNode) {
            ripple.parentNode.removeChild(ripple);
        }
    }, 600);
}

// Scroll progress indicator
function initializeScrollProgress() {
    const progressBar = document.querySelector('.md-progress');
    if (!progressBar) return;

    function updateProgress() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.body.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        progressBar.style.width = scrollPercent + '%';
    }

    window.addEventListener('scroll', updateProgress);
    updateProgress();
}

// Back to top button
function initializeBackToTop() {
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '↑';
    backToTopButton.className = 'back-to-top';
    backToTopButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        background: var(--sfai-primary);
        color: white;
        border: none;
        border-radius: 50%;
        font-size: 20px;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;

    document.body.appendChild(backToTopButton);

    // Show/hide based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.opacity = '1';
            backToTopButton.style.visibility = 'visible';
        } else {
            backToTopButton.style.opacity = '0';
            backToTopButton.style.visibility = 'hidden';
        }
    });

    // Smooth scroll to top
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Enhanced code copy buttons
function initializeCodeCopyButtons() {
    // Add copy buttons to code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(function(codeBlock) {
        const pre = codeBlock.parentElement;
        if (pre.querySelector('.copy-button')) return; // Already has copy button

        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '📋';
        copyButton.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: var(--sfai-primary);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
            cursor: pointer;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        `;

        pre.style.position = 'relative';
        pre.appendChild(copyButton);

        copyButton.addEventListener('click', function() {
            navigator.clipboard.writeText(codeBlock.textContent).then(function() {
                copyButton.innerHTML = '✅';
                setTimeout(function() {
                    copyButton.innerHTML = '📋';
                }, 2000);
            });
        });

        copyButton.addEventListener('mouseenter', function() {
            copyButton.style.opacity = '1';
        });

        copyButton.addEventListener('mouseleave', function() {
            copyButton.style.opacity = '0.7';
        });
    });
}

// Simple notebook enhancements
function initializeNotebookEnhancements() {
    const notebooks = document.querySelectorAll('.jupyter-notebook');

    notebooks.forEach(function(notebook) {
        // Add notebook banner if first element is h1
        const firstH1 = notebook.querySelector('h1');
        if (firstH1) {
            firstH1.style.cssText = `
                background: linear-gradient(135deg, var(--sfai-primary), var(--sfai-accent));
                color: white;
                margin: 0;
                padding: 20px;
                font-size: 1.5rem;
                font-weight: 600;
            `;
        }

        // Add download button for notebooks
        addNotebookDownloadButton(notebook);

        // Enhance output areas
        enhanceOutputAreas(notebook);

        // Add staggered animation to cells
        addCellAnimations(notebook);
    });
}

// Add staggered animations to notebook cells
function addCellAnimations(notebook) {
    const cells = notebook.querySelectorAll('.jp-Cell');
    cells.forEach(function(cell, index) {
        cell.style.animationDelay = (index * 0.1) + 's';
        cell.style.opacity = '0';
        cell.style.transform = 'translateY(20px)';

        // Trigger animation when in viewport
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'cellSlideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        observer.observe(cell);
    });
}

// Add download button for notebooks
function addNotebookDownloadButton(notebook) {
    const downloadButton = document.createElement('a');
    downloadButton.innerHTML = '⬇️ Download Notebook';
    downloadButton.className = 'notebook-download-btn';
    downloadButton.style.cssText = `
        position: absolute;
        top: 10px;
        right: 10px;
        background: rgba(255,255,255,0.2);
        color: white;
        text-decoration: none;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.9rem;
        transition: background 0.3s ease;
        z-index: 10;
    `;

    // Try to find the notebook file path from the current URL
    const currentPath = window.location.pathname;
    const notebookPath = currentPath.replace(/\/$/, '') + '.ipynb';
    downloadButton.href = notebookPath;
    downloadButton.download = notebookPath.split('/').pop();

    downloadButton.addEventListener('mouseenter', function() {
        downloadButton.style.background = 'rgba(255,255,255,0.3)';
    });

    downloadButton.addEventListener('mouseleave', function() {
        downloadButton.style.background = 'rgba(255,255,255,0.2)';
    });

    // Add to the first h1 if it exists
    const firstH1 = notebook.querySelector('h1');
    if (firstH1) {
        firstH1.style.position = 'relative';
        firstH1.appendChild(downloadButton);
    }
}

// Simple output area enhancements
function enhanceOutputAreas(notebook) {
    const outputAreas = notebook.querySelectorAll('.jp-OutputArea-output');

    outputAreas.forEach(function(output) {
        // Add subtle styling to long outputs
        if (output.scrollHeight > 200) {
            output.style.cssText = `
                max-height: 200px;
                overflow-y: auto;
                border: 1px solid var(--sfai-border);
                border-radius: 4px;
                padding: 8px;
                background: var(--sfai-surface);
            `;
        }
    });
}

// Search enhancements
function initializeSearchEnhancements() {
    const searchInput = document.querySelector('.md-search__input');
    if (!searchInput) return;

    // Add search placeholder enhancement
    searchInput.placeholder = 'Search SFAI SDK docs...';

    // Add search shortcuts
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
        }

        if (e.key === 'Escape' && document.activeElement === searchInput) {
            searchInput.blur();
        }
    });
}

// Smooth animations
function initializeAnimations() {
    // Add fade-in animation to main content
    const content = document.querySelector('.md-content__inner');
    if (content) {
        content.style.animation = 'slideUpFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    }

    // Add hover effects to navigation items
    const navItems = document.querySelectorAll('.md-nav__link');
    navItems.forEach(function(item) {
        item.addEventListener('mouseenter', function() {
            item.style.transform = 'translateX(4px)';
            item.style.transition = 'transform 0.2s ease';
        });

        item.addEventListener('mouseleave', function() {
            item.style.transform = 'translateX(0)';
        });
    });

    // Add intersection observer for elements
    const animatedElements = document.querySelectorAll('.md-typeset .admonition, .md-typeset table');
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'slideUpFadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    animatedElements.forEach(function(element) {
        observer.observe(element);
    });
}

// Utility function for smooth scrolling
function smoothScrollTo(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUpFadeIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes cellSlideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }

    .back-to-top:hover {
        background: var(--sfai-primary-dark) !important;
        transform: translateY(-2px);
    }

    .copy-button:hover {
        transform: scale(1.05);
    }

    .notebook-download-btn:hover {
        transform: translateY(-1px);
    }

    /* Enhanced tab transitions */
    .md-tabs__link {
        position: relative;
        overflow: hidden;
    }

    .md-content__inner {
        transition: opacity 0.3s ease, transform 0.3s ease;
    }
`;
document.head.appendChild(style);
