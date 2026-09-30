import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import App from '../App';

describe('ProjectLens app',()=>{beforeEach(()=>localStorage.clear());it('shows the premium demo login',()=>{render(<App/>);expect(screen.getByText('Complex projects.')).toBeInTheDocument();expect(screen.getByText('Enter workspace')).toBeInTheDocument()})});

