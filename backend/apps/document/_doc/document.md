# Document app guide
## Document type attributes
### reserved keywords
The keywords above cannot be used as document type attribute codes
* `owner`\
It identifies attribute storing **document owner** id. In most cases it will be client id (`user_client` table)

## Creating document 
### Attibutes obligatory for creating document
* `owner` - owner of document. Mostly it going to be client (`user_client` table)
* 