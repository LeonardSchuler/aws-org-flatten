Lists all organizational units, AWS accounts and their parent id in an AWS organization.

The script generates a Pandas dataframe of the form.

```
                   id                      name                 type         parent_id
0              r-xxxx                      xxxx                 ROOT
1             ou-yyyy                      yyyy  ORGANIZATIONAL_UNIT           r-xxxx
2        012345678910                      zzzz              ACCOUNT           ou-yyyy
...               ...                       ...                  ...               ...
```
