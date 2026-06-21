import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const NavContainer = styled.nav`
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const NavLink = styled(Link)`
  color: rgba(255, 255, 255, 0.78);
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.18s ease;
  font-weight: 500;
  line-height: 1;

  &:hover {
    background: rgba(255, 255, 255, 0.08);
    color: white;
  }

  &.active {
    background: rgba(14, 165, 233, 0.22);
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
