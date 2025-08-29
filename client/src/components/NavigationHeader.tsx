import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { NavigationHeaderStyles as styles } from '../cssmodules';

const NavigationHeader: React.FC = () => {
  const location = useLocation();
  const isMainPage = location.pathname === '/';
  const isHistoryPage = location.pathname === '/history';

  return (
    <header className={styles.navigationHeader}>
      <div className={styles.navContainer}>
        <div className={styles.navBrand}>
          <Link to="/" className={styles.brandLink}>
            🤖 AI Quiz Generator
          </Link>
        </div>
        
        <nav className={styles.navMenu}>
          <Link 
            to="/" 
            className={`${styles.navLink} ${isMainPage ? styles.active : ''}`}
          >
            🏠 Home
          </Link>
          <Link 
            to="/history" 
            className={`${styles.navLink} ${isHistoryPage ? styles.active : ''}`}
          >
            📚 Quiz History
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default NavigationHeader;
