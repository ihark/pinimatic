DELETE
FROM 
  public.taggit_tag 
WHERE 
  taggit_tag.id NOT IN 
  (SELECT tag_id 
     FROM taggit_taggeditem);