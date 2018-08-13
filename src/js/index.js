// @flow

import * as React from 'react';
import * as ReactDOM from 'react-dom';
import IconSettings from '@salesforce/design-system-react/components/icon-settings';
import logger from 'redux-logger';
import utilitySprite from '@salesforce-ux/design-system/assets/icons/utility-sprite/svg/symbols.svg';
import { Provider } from 'react-redux';
import { composeWithDevTools } from 'redux-devtools-extension';
import { combineReducers, createStore, applyMiddleware } from 'redux';

import Footer from './components/footer';
import Header from './components/header';
import { cache, persistMiddleware } from './utils/caching';
import userReducer from './accounts/reducer';

const MD_logo = require('images/metadeploy-logo.png');
const SF_logo = require('images/salesforce-logo.png');

const App = () => (
  <div>
    <Header logoSrc={MD_logo} />
    <Footer logoSrc={SF_logo} />
  </div>
);

cache.getAll().then(data => {
  const appStore = createStore(
    combineReducers({
      user: userReducer,
    }),
    data,
    composeWithDevTools(applyMiddleware(persistMiddleware, logger)),
  );

  const el = document.getElementById('app');
  if (el) {
    ReactDOM.render(
      <IconSettings utilitySprite={utilitySprite}>
        <Provider store={appStore}>
          <App />
        </Provider>
      </IconSettings>,
      el,
    );
  }
});
