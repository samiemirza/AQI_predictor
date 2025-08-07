import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const NavContainer = styled.nav`
  margin-left: auto;
  display: flex;
  align-items: center;
`;

const NavLink = styled(Link)`
  color: white;
  text-decoration: none;
  padding: 12px 20px;
  margin: 0 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-weight: 500;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
  }
  
  &.active {
    background: rgba(255, 255, 255, 0.2);
    color: white;
  }
`;

const Navigation = () => {
  const location = useLocation();

  return (
    <NavContainer>
      <NavLink 
        to="/" 
        className={location.pathname === '/' ? 'active' : ''}
      >
        Home
      </NavLink>
      <NavLink 
        to="/about" 
        className={location.pathname === '/about' ? 'active' : ''}
      >
        About
      </NavLink>
    </NavContainer>
  );
};

export default Navigation; 