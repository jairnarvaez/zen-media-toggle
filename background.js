let port = null;
let previousTabId = null;
let previousWindowId = null;

connectNative();

function connectNative() {
  try {
    port = browser.runtime.connectNative("media_tab_controller");
    port.onMessage.addListener((message) => {
      
      if (message.command === "switch_to_media") {
        switchToMediaTab();
      } else if (message.command === "get_media_tabs") {
        getMediaTabs();
      } else if (message.command === "switch_to_tab") {
        switchToTabById(message.tabId);
      } else if (message.command === "toggle") {
        toggleMediaTab();
      }
    });
    
    port.onDisconnect.addListener(() => {
      console.log("Desconectado de la aplicación nativa");
      port = null;
    });
    
    console.log("Conectado a la aplicación nativa");
  } catch (error) {
    console.error("Error conectando con aplicación nativa:", error);
  }
}

function switchToMediaTab() {

  browser.tabs.query({ active: true, currentWindow: true }).then(currentTabs => {
    if (currentTabs.length > 0) {
      previousTabId = currentTabs[0].id;
      previousWindowId = currentTabs[0].windowId;
    }
    
    browser.tabs.query({}).then(tabs => {
      const mediaTab = tabs.find(tab => tab.audible);
      
      if (mediaTab) {
        browser.tabs.update(mediaTab.id, { active: true });
        browser.windows.update(mediaTab.windowId, { focused: true });
        
        if (port) {
          port.postMessage({ 
            success: true, 
            tabId: mediaTab.id, 
            title: mediaTab.title,
            previousTabId: previousTabId
          });
        }
      } else {
        if (port) {
          port.postMessage({ 
            success: false, 
            message: "No hay pestañas reproduciendo medios" 
          });
        }
      }
    });
  });
}

function getMediaTabs() {
  browser.tabs.query({}).then(tabs => {
    const mediaTabs = tabs.filter(tab => tab.audible).map(tab => ({
      id: tab.id,
      title: tab.title,
      url: tab.url
    }));
    
    if (port) {
      port.postMessage({ 
        command: "media_tabs_list",
        tabs: mediaTabs 
      });
    }
  });
}

function switchToTabById(tabId) {
  browser.tabs.query({ active: true, currentWindow: true }).then(currentTabs => {
    if (currentTabs.length > 0 && currentTabs[0].id !== tabId) {
      previousTabId = currentTabs[0].id;
      previousWindowId = currentTabs[0].windowId;
    }
    
    browser.tabs.update(tabId, { active: true }).then(() => {
      browser.tabs.get(tabId).then(tab => {
        browser.windows.update(tab.windowId, { focused: true });
        
        if (port) {
          port.postMessage({ 
            success: true, 
            tabId: tab.id, 
            title: tab.title,
            previousTabId: previousTabId
          });
        }
      });
    }).catch(error => {
      if (port) {
        port.postMessage({ 
          success: false, 
          message: "No se pudo cambiar a la pestaña" 
        });
      }
    });
  });
}

function toggleMediaTab() {
  browser.tabs.query({ active: true, currentWindow: true }).then(currentTabs => {
    if (currentTabs.length === 0) return;
    
    const currentTab = currentTabs[0];
    
    if (currentTab.audible && previousTabId !== null) {
      browser.tabs.get(previousTabId).then(prevTab => {
        const tempTabId = currentTab.id;
        const tempWindowId = currentTab.windowId;
        
        browser.tabs.update(previousTabId, { active: true });
        browser.windows.update(previousWindowId, { focused: true });
        
        if (port) {
          port.postMessage({
            success: true,
            action: "toggled_back",
            tabId: previousTabId,
            title: prevTab.title
          });
        }
        
        previousTabId = tempTabId;
        previousWindowId = tempWindowId;
        
      }).catch(error => {
        previousTabId = null;
        previousWindowId = null;
        switchToMediaTab();
      });
    } else {
      switchToMediaTab();
    }
  });
}

browser.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.audible === true) {
    browser.tabs.query({ active: true, currentWindow: true }).then(currentTabs => {
      if (currentTabs.length > 0 && currentTabs[0].id !== tabId) {
        previousTabId = currentTabs[0].id;
        previousWindowId = currentTabs[0].windowId;
      }
      
      browser.tabs.update(tabId, { active: true });
      
      if (port) {
        port.postMessage({
          event: "media_started",
          tabId: tabId,
          title: tab.title,
          previousTabId: previousTabId
        });
      }
    });
  }
});

browser.browserAction.onClicked.addListener(() => {
  switchToMediaTab();
});
