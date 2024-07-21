# DOCUMENT PROCESS FLOW
todo: add process flow structures description
## ACTIONS
## Common actions
Common actions are defined in `DocumentTypeStatus.common_actions JSONField` type column in the form of `json` dict.

### copy action

Action just set value of the attribute specified as the key to the attribute specified as value

```json
{
  "copy": {
    "1256": "3293",
    "1257": "3275",
    "3352": "3273",
    "3367": "3434",
    "3379": "3297",
    "3380": "3295",
    "3381": "3325",
    "3382": "3326",
    "3423": "3262",
    "3424": "3266",
    "3425": "3310",
    "3427": "3410",
    "3428": "3411",
    "3430": "3392"
  }
}
```

## Actions called from "_outside_" classes - lets call them "_external actions_"
These actions are stored in `DocumentTypeStatus.action` and `DocumentTypeStatus.action_class` fields
`action field` stores action name to be triggered
`action_class` field stores full path to class 

Example:\
`action: create_loan`\
`action_class: apps.product.action.ProductAction`

## Actions execution order
First are the common actions executed, then "external":
1. common actions
2. external actions

## Actions parameters
`user` - user logged in\
`document` - instance of `Document` object being processed
