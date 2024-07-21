# Swith to another theme like swap dark-light themes
first define css styles for default (light) theme
```css
.subsection-container {
  background-color: #efefef;
  margin: 0;
  padding: 15px;
  border: 2px dashed #8c8c8c;
  border-radius: 5px;
  margin-bottom: 15px;
}
```
then define styles for the "dark" theme
```css
[data-theme="dark"] {
  .subsection-container {
    background-color: #000c1a;
  }
}
```
last is to set the theme on documentElement (root of the document)

```javascript
document.documentElement.setAttribute('data-theme', 'dark');
```
that's it! :blush: