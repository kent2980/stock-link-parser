import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="header-logo">
          <h1>XBRL財務諸表ビューア</h1>
        </Link>
        <nav className="header-nav">
          <Link to="/" className="nav-link">
            銘柄一覧
          </Link>
        </nav>
      </div>
    </header>
  );
};

export default Header;
