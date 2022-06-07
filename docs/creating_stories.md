# How To Create Stories

This section is under development and will be updated soon.

## Story Folder
Story folders contain of a "info.ttl" containing the metadata, chapter folders and a db folder where data is saved.

1. Create a subfolder in "stories". Use your story's name as the folder's name or a short version of it. The story's folder name will be used in the startmenu as list item.
2. Create a Turtle file "info.ttl" that defines the metadata of your story:
   * Metadata includes title, description, trailer (image), tags and color schema.
   * Metadata is retrieved via the requests ["get_info.rq"](/requests/get_info.rq) and ["get_authors.rq"](/requests/get_authors.rq)
   * The color schema consists of three colors for foreground, background and highlighting. Use online tools like https://mycolor.space/ to select adequate colors.
   * Just copy the demo's ["info.ttl"](/stories/demo/info.ttl) and change the values according to your story.
3. Create a subfolder "db" containing Turtle files "locations.ttl" and "people.ttl".
   * "locations.ttl" and "people.ttl" contains all the locations you will visit in a story and all the people you will meet (including the player himself).
   * Just copy the demo's ["locations.ttl"](/stories/demo/db/locations.ttl) and ["people.ttl"](/stories/demo/db/people.ttl), and change the values according to your story.

## Creating Chapters and Episodes
A chapter folder contains the data that is used to generate an interactive chapter of the story. The data is stored as a single or multiple Turtle files as all data is loaded as a single Graph. This is important as all files share the same blank node identifiers. Nonetheless, we recommend to use one Turtle file for defining the chapter's episode sequence and one Turtle file each for a new episode. The order of chapters is defined by the numeric value before the underline in the chapter folder's name.

1. Create a folder with the naming convention "[0-9]*_(\w|\s)+", e.g. "1_The Beginning".
2. Create a chapter's bag according to [demo chapter 1](/stories/demo/1_The%20Interview/chapter.ttl)
   * [rdf:Bag](https://www.w3.org/TR/rdf-schema/#ch_bag) is an unordered list, because the player can decide the order of the episodes.
```turtle
:chapter1   :hasEpisodes    _:b0     .
_:b0        rdf:type        rdf:Bag  ;
            rdf:_1          :ep1     ;
            rdf:_2          :ep2     .
```
1. Create episode sequences according to [demo episode 1](/stories/demo/1_The%20Interview/episode_1.ttl)
   * Data is retrieved via request ["get_episodes.rq"](/requests/get_episodes.rq).
   * [rdf:Sequence](https://www.w3.org/TR/rdf-schema/#ch_seq) is an ordered list, because the order of scenes is fixed.
```turtle
:ep1        :hasScenes      _:seq   .
_:seq      rdf:type         rdf:Seq ;
            rdf:_1          :scene1 ;
            rdf:_2          :scene2 ;
```

## Creating Scenes
Episodes consist of one or multiple scenes. At the moment three scene types exist: MapScene, TalkScene, QueryScene. Data to generate scenes is retrieved via request ["get_scenes.rq"](/requests/get_scenes.rq) 
* The MapScene is automatically generated as first scene of an chapter and cannot be manually added. 
* TalkScenes are used to add triples to the player's knowledge base. 
* QueryScenes are used to test the player's ability to write SPARQL queries that retrieve solution sequences from the current knowledge base.

### Creating TalkScenes
TalkScenes represent a mono- or dialogue of people. Each TalkScene consists of a talk item sequence ([rdf:Sequence](https://www.w3.org/TR/rdf-schema/#ch_seq)) and a single background. A talk item consists of a speaker, the spoken text and hidden RDF triples. Talk items are retrieved via request ["get_talk.rq"](/requests/get_talk.rq) and hidden triples are retrieved via ["get_statements_in_talk_item.rq"](/requests/get_statements_in_talk_item.rq). 

Each Triple set is hidden behind three keywords/labels that are part of the spoken text. Keywords are identified by brackets. Keywords are stored as [rdf:List](https://www.w3.org/TR/rdf-schema/#ch_list) and orderd according subject, predicate, object:
```turtle
[
    :hasText     "[I] [am] [Jim Gordan]. [I] am [your] [supervisor]. It is nice to finally meet you." ;
    :hidden [
        :labels ("I" "am" "Jim Gordan");
        ...
        ]
    :hidden [
        :labels ("I" "your" "supervisor");
        ...
        ]
]
```

If you want to use a keyword multiple times with different hidden terms, you can also define an alias for the keyword with entailing parenthesis:
```turtle
[
    :hasText     "[I] [am] [Jim Gordan]. [I](#2) am [your] [supervisor]. It is nice to finally meet you." ;
    :hidden [
        :labels ("I" "am" "Jim Gordan");
        ...
        ]
    :hidden [
        :labels ("#2" "your" "supervisor");
        ...
        ]
]
```

There are two options to denote hidden triples:
* If there is only a single triple hidden for a keyword set that you can use an [rdf:Statement](https://www.w3.org/TR/rdf-schema/#ch_statement) with [rdf:subject](https://www.w3.org/TR/rdf-schema/#ch_subject), [rdf:predicate](https://www.w3.org/TR/rdf-schema/#ch_predicate), and [rdf:object](https://www.w3.org/TR/rdf-schema/#ch_object). Optionally, you can also define namespaces:
```turtle
[
    :hasText     "[I] [am] [Jim Gordan]. [I](#2) am [your] [supervisor]. It is nice to finally meet you." ;
    :hidden [
        :labels ("I" "am" "Jim Gordan");
        :namespaces    '''
        PREFIX ex:      <https://www.example.org/>
        PREFIX foaf:    <http://xmlns.com/foaf/spec/#>
        ''''         ;
        rdf:subject    <https://www.example.org/jim>                   ;
        rdf:predicate  <http://xmlns.com/foaf/spec/#name>          ; 
        rdf:object     "Jim Gordan"     
        ]
]
```
* If there are multiple triples hidden for a keyword set (or you just prefer this option), you can embed a SPARQL update. Updates are prioritized by RDeF when both options are given:
```turtle
[
    :hasText     "[I] [am] [Jim Gordan]. [I](#2) am [your] [supervisor]. It is nice to finally meet you." ;
    :hidden [
        :labels ("I" "am" "Jim Gordan");
        :update '''
            PREFIX ex: <https://www.example.org/>
            PREFIX foaf: <http://xmlns.com/foaf/spec/#>
            
            INSERT DATA {
            ex:jim      foaf:name   "Jim Gordan" .
            }
        ''' 
        ]
]
```


### Creating QueryScenes
QueryScenes can be used to check, if the player has understood the current knowledge base. A QueryScene consists of a question and a markup query. The result set of the markup query will be compared with the result set of the player's SPARQL query. In SPARQL, the ?-symbol and the $-symbol can be used interchangeable. However in RDeF,the markup query uses the $-symbol to define which elements should be available as draggables or replaced with a blank. This means only the ?-symbol can be used to declare a variable.

```turtle
:scene3     rdf:type        :QueryScene  ;
            :question       "What is the supervisor's name of Jack?";
            :markup_query   """
                            SELECT ?name 
                            WHERE {
                                ?supervisor :superviserOf  $:jack ;
                                            $foaf:name       ?name .
                                }
                            """ .
```

## Resources
It is important that all media files you are using are under public domain license:
* There are several websites where you can generate fake persons, e.g., https://boredhumans.com/faces.php.
