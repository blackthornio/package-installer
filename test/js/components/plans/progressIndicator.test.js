import React from 'react';
import { render } from 'react-testing-library';

import ProgressIndicator from 'components/plans/progressIndicator';

describe('<ProgressIndicator />', () => {
  const setup = options => {
    const defaults = {
      userLoggedIn: true,
      preflightStatus: null,
      preflightIsValid: true,
      preflightIsReady: false,
    };
    const opts = { ...defaults, ...options };
    const { getByText } = render(
      <ProgressIndicator
        userLoggedIn={opts.userLoggedIn}
        preflightStatus={opts.preflightStatus}
        preflightIsValid={opts.preflightIsValid}
        preflightIsReady={opts.preflightIsReady}
      />,
    );
    return { getByText };
  };

  describe('not logged in', () => {
    test('shows no steps complete', () => {
      const { getByText } = setup({
        userLoggedIn: false,
      });

      expect(getByText('Step 1: Log in')).toBeVisible();
      expect(getByText('Step 2: Run pre-install validation')).toBeVisible();
      expect(
        getByText('Step 3: Pre-install validation complete'),
      ).toBeVisible();
    });
  });

  describe('logged in, no preflight', () => {
    test('shows first step complete', () => {
      const { getByText } = setup();

      expect(getByText('Step 1: Log in - Completed')).toBeVisible();
      expect(getByText('Step 2: Run pre-install validation')).toBeVisible();
      expect(
        getByText('Step 3: Pre-install validation complete'),
      ).toBeVisible();
    });
  });

  describe('preflight started', () => {
    test('shows first two steps complete', () => {
      const { getByText } = setup({
        preflightStatus: 'started',
      });

      expect(getByText('Step 1: Log in - Completed')).toBeVisible();
      expect(
        getByText('Step 2: Run pre-install validation - Completed'),
      ).toBeVisible();
      expect(
        getByText('Step 3: Pre-install validation complete'),
      ).toBeVisible();
    });
  });

  describe('preflight invalid', () => {
    test('shows first step complete', () => {
      const { getByText } = setup({
        preflightStatus: 'complete',
        preflightIsValid: false,
      });

      expect(getByText('Step 1: Log in - Completed')).toBeVisible();
      expect(getByText('Step 2: Run pre-install validation')).toBeVisible();
      expect(
        getByText('Step 3: Pre-install validation complete'),
      ).toBeVisible();
    });
  });

  describe('preflight complete and is_ready', () => {
    test('shows all steps complete', () => {
      const { getByText } = setup({
        preflightStatus: 'complete',
        preflightIsReady: true,
      });

      expect(getByText('Step 1: Log in - Completed')).toBeVisible();
      expect(
        getByText('Step 2: Run pre-install validation - Completed'),
      ).toBeVisible();
      expect(
        getByText('Step 3: Pre-install validation complete - Completed'),
      ).toBeVisible();
    });
  });

  describe('preflight complete with errors', () => {
    test('shows error step', () => {
      const { getByText } = setup({
        preflightStatus: 'complete',
      });

      expect(getByText('Step 1: Log in - Completed')).toBeVisible();
      expect(
        getByText('Step 2: Run pre-install validation - Completed'),
      ).toBeVisible();
      expect(
        getByText('Step 3: Pre-install validation complete - Error'),
      ).toBeVisible();
    });
  });
});