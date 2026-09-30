# Historical and Technical Audit of the Dance Competition “Skating System”

## Executive conclusion

### Recommended authority for a Canadian implementation

For a **Canadian International Style ballroom event**, the strongest presently supportable authority is a **two-document chain**, rather than Arthur Dawson's historical booklet or an unattributed PDF standing alone:

1. **Canada DanceSport, _Rule Book Effective August 15, 2025_**, Rule 20.06, because the current Canadian national rulebook expressly says that judges are to follow the Skating System **“as defined from time to time by WDSF”** for Championship finals, while allowing another system if Canada DanceSport approves it. The same rulebook requires a marking card containing an error or omission to be returned to the judge for correction. Rule 20 is expressly identified as applying to International Style. citeturn18view1
2. **World DanceSport Federation's current Rules page and the document it currently links as _The Skating System_**. WDSF's 2026 rules page lists that document in its Competition materials alongside the 2026 Competition Rules; the WDSF document URL presently redirects to a WDSF Box-hosted file. citeturn6view0turn7view0

The resulting authority chain is therefore:

> **Canada DanceSport Rule 20.06 → the WDSF definition in force → WDSF's currently linked _The Skating System_.**

That is a substantially stronger basis for contemporary Canadian software than saying “we implemented the 1963 Dawson rules” or “we found a PDF called _The Skating System_.” Canada DanceSport is the Canadian WDSF member body and describes itself as the national authority for its governed DanceSport activities; its current rulebook incorporates WDSF's definition dynamically. citeturn14view0turn18view0

For an **independent** Canadian event, however, CDS/WDSF rules do not become the event's rules merely because the event occurs in Canada. The defensible approach is for the organizer's own published rules to **adopt a specific reference deliberately**. I would recommend wording that pins the technical definition rather than merely saying “Skating System,” for example: the event uses Rules 5–8 of the WDSF-linked _The Skating System_, as archived by the organizer on a stated date, subject to enumerated local exceptions. This matters because Canada DanceSport itself uses the moving phrase “from time to time”; that is sensible for federation governance but undesirable as a software regression-test specification. citeturn18view1

There is one provenance weakness in this recommendation: **the WDSF-linked eleven-rule explanatory document is undated and unattributed in the copy I was able to inspect.** WDSF's current listing proves present endorsement, not original authorship or original publication date. I found no sound basis for calling that particular worked-example PDF “the Dawson 1963 edition,” nor for attributing its prose to WDSF as original author. citeturn6view0turn11view0

The best **dated, federation-branded corroborating copy** I found is Svenska Danssportförbundet's:

> **_The Skating System — Bedömningssystemet för Standard, Latin och 10-dans_, Version 1, 2024-09-01.**

Its cover identifies Svenska Danssportförbundet, the exact version, and date. Its Rules 5–8, worked examples, competitor numbers, and operative procedures match the WDSF-linked teaching text in the portions compared. citeturn28view0turn27view0 It therefore makes an excellent **audit witness**, but it is Swedish authority, not the source that should govern a Canadian event.

### Historical conclusion

The historical evidence is less clean than many online summaries imply.

The most important early publication I could substantiate bibliographically is **Arthur Dawson, _The Skating system. Working out the marks in ballroom dancing championships_ (1963)**. Xavier Mora's 2001 study identifies it as published by the **Official Board of Ballroom Dancing**, predecessor of today's British Dance Council, and calls it the most highly regarded exposition of the completed system. Mora also states that the system reached its present separate-dance form in the late 1940s and was completed in **1956 with Rule 11**. citeturn22view0turn24view0 The British Dance Council independently confirms that it began as the Official Board of Ballroom Dancing in 1929 and later changed its name. citeturn29search3turn29search33

I would **not**, on the evidence located, state categorically that “the Skating System was invented in 1937.” A widely repeated secondary history gives 1937 and attributes the original majority principle to Dawson, whereas Mora places the first entry of the majority criterion into ballroom competition in **1938 at the Star Championships**, with the broader method developing later. citeturn29search1turn22view0 No contemporaneous 1937/1938 Official Board minutes, rules circular, _Dancing Times_ notice, or equivalent primary artifact was located in this audit. The discrepancy should remain explicit.

### Rules 5–8 conclusion

For the immediate single-dance implementation, the good news is that I found **no supported material algorithmic change in Rules 5–8 between the current WDSF-linked text, the dated 2024 Swedish federation version, and Xavier Mora's formalization of the traditional system**. Mora specifically concludes that the Traditional, Simplified/Majoritätssystem, and his proposed Improved system produce the **same separate-dance ordering under Rules 1–8**; their differences arise when combining dances. citeturn24view0

The operative procedure supported by the current federation text is:

\[
M=\left\lfloor\frac{J}{2}\right\rfloor+1
\]

for a strict majority; with your always-odd panel this is simply \((J+1)/2\). At cumulative threshold \(t\), count each competitor's judge ranks \(\le t\). Once competitors have a majority, a larger majority prevails; equal majorities are resolved by the lower sum of the qualifying marks; an unresolved tied subgroup alone advances to the next cumulative column; if nobody has a majority, all still-unplaced competitors advance to the next column; and an exact tie remaining at the last possible column produces the arithmetic mean of the consecutive positions occupied. citeturn27view0turn28view2

Two apparent errors in the modern teaching text are **not rule changes**:

* In the Rule 6 example, after explicitly advancing to “5th and higher,” the prose says competitor 65 has five “4th place and higher” marks. The published ranks give only three marks \(\le4\) but five marks \(\le5\); the table and outcome therefore require “5th place and higher.” The same defect appears in the textual family inspected. citeturn27view0
* In the Rule 7 continuation, one sentence refers to competitors “#74, #85, and #76”; the example contains competitors 71–76, so #85 is plainly #75. citeturn27view0

Those are precisely the kind of transcription/typesetting defects that should be documented in a software audit instead of encoded literally.

## Edition and source timeline

The table separates an actual rule publication from evidence about adoption. “Not inspected” means I found evidence establishing the work's existence and provenance but did not obtain a source copy sufficient for page-by-page verification.

| Date | Exact title/version | Issuer/author | Jurisdiction | Source status | Rules / relevant pages | Material significance | Direct source | Archive |
|---|---|---|---|---|---|---|---|---|
| **1937 or 1938** | No primary publication located; early majority-principle use | Commonly attributed to Arthur Dawson / Official Board lineage | Great Britain | Historical event; evidence presently secondary | Precursor, not yet established as the complete 11-rule system | Secondary accounts conflict: one gives **1937** introduction; Mora gives **1938 Star Championships** for entry of the majority criterion. Do not collapse these into a certain publication date. citeturn29search1turn22view0 | No contemporaneous source located | Not established |
| **Late 1940s** | No title located | Official Board of Ballroom Dancing | Great Britain | Historical adoption reported by Mora | Separate-dance majority method corresponding to later Rules 5–8 | Mora says the majority criterion acquired its present broad scope when the Official Board adopted the method at the end of the 1940s. citeturn22view0 | Evidence: [Mora 2001 PDF](https://mat.uab.cat/~xmora/escrutini/skating2en.pdf) | Not established |
| **1956** | No title located | Official Board of Ballroom Dancing | Great Britain | Historical rule revision reported by Mora | Completion through Rule 11 | Mora says the system's present form was completed when Rule 11 was introduced in 1956. This dates completion of Rules 1–11, not necessarily publication of a booklet. citeturn22view0 | Evidence: [Mora 2001 PDF](https://mat.uab.cat/~xmora/escrutini/skating2en.pdf) | Not established |
| **1963** | **_The Skating system. Working out the marks in ballroom dancing championships_** | **Arthur Dawson**; published by Official Board of Ballroom Dancing according to Mora | Great Britain / ballroom | Primary official exposition by bibliographic description; copy not inspected | Complete traditional system; precise Rules 5–8 pages not established. Mora cites Dawson Example N at pp. 14–15. | Historically strongest identified canonical exposition. Mora says later anonymous abridgement was based on it and says his systematic formulation agrees with Dawson in the cases Dawson covers. citeturn22view0turn24view0 | No verified public scan found; bibliographic record in [Mora](https://mat.uab.cat/~xmora/escrutini/skating2en.pdf) | Not established |
| **1981** | **_Skating System_** | International Council of Amateur Dancers | International amateur ballroom | Official reproduction, according to Mora; not inspected | Abridged traditional Skating exposition | Mora explicitly identifies this as a reproduction of an **anonymous abridgement based on Dawson 1963**. citeturn24view0 | No verified accessible copy found | Not established |
| **1991** | **_Grundlagen der Turnierleitung_, 2. Auflage** | Deutscher Tanzsportverband (DTV) | Germany | Official federation handbook; bibliographic evidence via Mora | Appendix pp. 10–24 according to Mora | Material because Mora reports that its systematic treatment disagrees with Dawson in at least one extreme case. The available evidence does **not** establish that the disagreement lies specifically within Rules 5–8 rather than elsewhere, so it should not be imported into the single-dance algorithm without obtaining the book. citeturn22view0turn24view0 | No current verified copy located | Not established |
| **Oct. 1993** | **_El sistema Skating_**, first edition | Xavier Mora; published by Asociación Española de Baile Deportivo y de Competición (AEBDC) | Spain | Analytical/secondary exposition published by national association | Full system analysis | First edition of Mora's systematic treatment; later expanded/reissued in English. citeturn24view0 | Bibliographic evidence in [2001 edition](https://mat.uab.cat/~xmora/escrutini/skating2en.pdf) | Not established |
| **1994** | **_Description of the skating system used to judge ballroom dance events_** | Richard M. Moroney | Ballroom | Unofficial/secondary web reproduction | Traditional system | Mora identifies it as another reproduction of the anonymous Dawson-based abridgement, so duplicated wording here is **not independent corroboration**. citeturn24view0 | Historical URLs are listed by Mora; current availability not verified | Not established |
| **1996** | **_Certified Correct. The dancesport scrutineer's rulebook and observer's guide to competition marks_** | Jeff Carlsen; Dancing Bear Publishing Company, Halifax, Canada | North America / ballroom | Secondary technical handbook; stated by Mora to be NDCA-endorsed | Skating/scrutineering system | Particularly relevant Canadian publication; Mora identifies Halifax publication and NDCA endorsement. Text not inspected, so no line-by-line Rules 5–8 comparison is claimed. citeturn24view0 | No verified full-text source located | Not established |
| **2000** | **_The mystical art of tabulating dancesport competition marks (The Skating System)_** | Jim Warren | DanceSport | Secondary teaching exposition | Full teaching treatment | One of the later expositions Mora lists after the Dawson-era material. It should be treated as explanatory, not as evidence of a new governing-rule edition. citeturn24view0 | Historical URL recorded by Mora: `http://www.csd.co.za/articles/scrutineer/Intro.htm` | Not established |
| **Jan. 2001** | **_Das Majoritätssystem_, in _Turnier- und Sportordnung des Deutschen Tanzsportverbandes e.V._, Stand Januar 2001** | DTV | Germany | Official federation rules | Appendix pp. 68–71 according to Mora | The important difference is **multi-dance**: Mora characterizes this simplified system as Rules 1–8 plus Rule 9, omitting traditional Rules 10–11. He says the separate-dance results under Rules 1–8 are the same. citeturn24view0 | Historical URL recorded by Mora; no current copy verified | Not established |
| **2001** | **_The A to Z of Scrutineering_** | Estelle Grassby | Great Britain | Secondary handbook, stated BDC-approved | Scrutineering / Skating | Material as a BDC-approved post-Dawson exposition, but not inspected here. citeturn24view0 | A current dance-book seller still lists the title, but no source text was located. citeturn25search10 | Not established |
| **July 2001** | **_THE SKATING SYSTEM_, 2nd edition** | Xavier Mora | International scholarly/technical analysis | Secondary analytical source | Rules 1–11 plus Simplified and Improved variants; history pp. 1–3, formulation pp. 4–5, conclusions p. 13, bibliography pp. 14–15 in the PDF | Crucial provenance source and useful formalization. It explicitly distinguishes traditional Rules 1–8,9,10,11 from alternative multi-dance systems and says all three variants agree in each separate dance. citeturn22view0turn24view0 | [Direct PDF](https://mat.uab.cat/~xmora/escrutini/skating2en.pdf) | No verified snapshot recorded in this audit |
| **2010-06-21** | **_Unraveling the Mystery of the Relative Placement Scoring System_** | Author not established from inspected page; hosted by World Swing Dance Council | Swing | Official WSDC-hosted technical explanation; related system, **not a numbered Skating edition** | RPSS; first article page establishes ordinal conversion, unique rankings, majority concept | Demonstrates the ballroom majority/ordinal family extending into swing under the name Relative Placement. The first page requires unique judge rankings and explains why odd panels work best. It does not establish a Dawson/WDSF publication lineage. citeturn26search3turn28view3 | [WSDC PDF](https://www.worldsdc.com/wp-content/uploads/2016/04/Relative_placement.pdf) | Not established |
| **Undated; current on WDSF site in 2026** | **_The Skating System_** | Original author/issuer **not identified in the document evidence obtained**; currently published/endorsed by WDSF | WDSF DanceSport | Current official WDSF-listed technical document | All **11 rules**; in accessible 22-page mirror Rule 5 p. 5, Rule 6 p. 6, Rule 7 pp. 7–8, Rule 8 pp. 9 onward | Best current international technical reference, but weak bibliographic metadata. Current WDSF endorsement is established; original authorship/date are not. citeturn6view0turn7view0turn9view0 | WDSF: `https://www.worlddancesport.org/Document/99473179446/The-Skating-System.pdf`; current Box target: `https://dancesport.app.box.com/s/w60qa4644xcfuggvq03ygjo3ksivwo1w`; accessible mirror: `https://madsf.mk/download_wdsf.php?file=6+-+The+Skating+System.pdf` | No dated WDSF snapshot verified |
| **2024-09-01** | **_The Skating System — Bedömningssystemet för Standard, Latin och 10-dans_, Version 1** | Svenska Danssportförbundet | Sweden / Standard, Latin, 10-dance | Official national-federation adaptation/reproduction | Rules 1–11; Rule 5 pp. 5–6, Rule 6 p. 6, Rule 7 pp. 7–8, Rule 8 pp. 8–9 | Dated and versioned reproduction of the same operative Rules 5–8 teaching text. No material Rules 5–8 change found; layout/page count differs from the 22-page WDSF-linked copy. citeturn28view0turn27view0 | [Direct PDF](https://www.danssport.se/media/z3jlnzuj/the-skating-system-slt-2024-09-01.pdf) | No separate archive verified |
| **Effective 2025-08-15; current website listing updated 2026-04-14** | **_CANADA DANCESPORT Rule Book Effective August 15, 2025_**, 2025–2026 English V2 | Canada DanceSport | Canada; Rule 20 applies International Style | Primary current Canadian rulebook | Incorporates Skating by reference: Rule 20.06, PDF p. 39 area; Schedule C also expressly says “The Skating System shall be employed” for Ten-Dance finals | Most relevant current Canadian governing source. It does not rewrite Rules 5–8; it delegates their definition to WDSF “from time to time.” citeturn16view0turn17view0turn18view0 | [Direct PDF](https://www.dancesport.ca/attachments/File/Rules/2025%20-%202026%20CDS%20Bylaws%20and%20Rule%20Book%20Eng%20with%20changes%20after%20all%20revisions%20August%2015,%202025%20V2.pdf) | No separate archive verified |

Two bibliographic cautions deserve emphasis. First, later secondary references disagree about details such as the 1963 Dawson booklet's publisher/imprint and even page count. Mora's bibliography says it was published by the Official Board; another later academic bibliography describes an ISTD/_Dancing Times_ association. I found no copy of the title page with which to adjudicate that discrepancy, so those extra imprint details should **not** yet be committed as fact. citeturn24view0turn25search5 Second, a website's upload date was not used as a document publication date anywhere above.

## Source genealogy

### The original line

The British Dance Council's own institutional history establishes the organizational continuity: the body began in 1929 as the **Official Board of Ballroom Dancing** and later became the British Dance Council. citeturn29search3turn29search33 Within that lineage, Mora's historical account places development in stages: early majority use in 1938, expansion to the broad majority method in the late 1940s, completion with Rule 11 in 1956, and Dawson's 1963 exposition of the completed system. citeturn22view0

Thus, the defensible genealogy is not:

> 1937 → a finished eleven-rule PDF.

It is closer to:

> **early majority principle → late-1940s expansion → 1956 completed eleven-rule system → Dawson's 1963 official exposition.**

The exact 1930s year remains unsettled on the evidence obtained.

### Dawson and the anonymous abridgement

Mora provides unusually useful provenance information. His bibliography identifies:

> Arthur Dawson, 1963, _The Skating system. Working out the marks in ballroom dancing championships_,

then separately identifies an **anonymous abridged exposition based on Dawson**. He says that abridgement was reproduced by the **International Council of Amateur Dancers in 1981** as _Skating System_ and again in Richard Moroney's 1994 description. citeturn24view0

That means identical language among those later reproductions would be genealogical copying, not independent corroboration. This directly supports the user's requested evidentiary rule: ten websites repeating the same paragraph are still one textual lineage.

### Later attempts to systematize it

Mora says Dawson and the anonymous abridgement use a case-oriented explanation and leave some extreme cases insufficiently explicit. He cites the German DTV handbook as an attempt at a comprehensive systematization but reports at least one disagreement with Dawson. Mora then says his own formulation was designed to cover all cases while agreeing with Dawson in every case Dawson explicitly considered. citeturn22view0

This makes the later literature useful in different ways:

**Dawson 1963** is historically authoritative; **Mora 2001** is algorithmically valuable; **DTV 1991** is evidence that edge-case interpretation has not always been universal; **Carlsen 1996** and **Grassby 2001** demonstrate later North American and British professional teaching traditions. Mora records Carlsen's Halifax publication as NDCA-endorsed and Grassby's book as BDC-approved. citeturn24view0

None of those facts, by themselves, makes those books the present Canadian governing authority.

### The modern eleven-rule PDF

The modern document commonly encountered simply as **_The Skating System_**, with eleven numbered rules and worked examples numbered 51–56, 61–66, 71–76, 81–86, is a distinct provenance problem.

What can be established is:

* WDSF **currently lists a document of exactly that title** on its official Rules page and sends the user through a WDSF document URL to a WDSF Box share. citeturn6view0turn7view0
* An accessible 22-page copy contains the eleven-rule structure and the worked examples in question. Its contents identify Rule 5 at p. 5, Rule 6 at p. 6, Rule 7 at p. 7, Rule 8 at p. 9, followed by Rules 9–11 and a final example. citeturn9view0turn11view0
* The 2024 Swedish federation publication reproduces the same operative prose, competitor numbers and examples, but adds Swedish federation branding, **Version 1**, the date **2024-09-01**, and different pagination. citeturn28view0turn27view0
* The same textual family also appears on explanatory dance websites. That is evidence of dissemination, not independent authority. citeturn8search4

What cannot presently be established is **who originally wrote or first issued this particular modern worked-example document**. Its current presence on WDSF's site establishes current endorsement, but not that WDSF was its original author, not that it dates from a particular WDSF/IDSF year, and certainly not that it is a facsimile of Dawson 1963.

The Swedish PDF and 22-page copy are also clearly **not identical PDF editions**: one is 19 pages and federation-branded/versioned, while the accessible 22-page version uses a different layout. They are, however, substantively the same Rules 5–8 teaching text. citeturn28view0turn27view0turn9view0

### Canadian and swing branches

Canada DanceSport does not create another algorithmic edition. Instead, it creates a **jurisdictional reference edge**: its current Rule 20.06 delegates the meaning of Skating to whatever WDSF defines from time to time. Schedule C separately requires the Skating System for Ten-Dance finals. citeturn18view0

World Swing Dance Council's **Relative Placement Scoring System** belongs in the broader genealogy of ordinal-majority dance scoring, but should not be mislabeled a WDSF/Dawson edition. The official WSDC-hosted document's first page says raw scores are converted into unique ordinal rankings, judges cannot tie competitors, and decisions are based on majority; it expressly discusses odd-numbered judging panels. citeturn28view3 That makes it highly relevant when auditing swing software, but it is a separate organizational rule source.

I found no comparably solid official **World Rock'n'Roll Confederation** source establishing that its current competition scoring is the eleven-rule Skating System. That gap is reported below rather than filled by inference.

## Rules 5–8 comparison matrix

The most important comparison is that **the material single-dance algorithm is unusually stable**, whereas provenance and multi-dance treatment vary much more.

| Version / authority | Majority and cumulative columns | Multiple majority | Equal majority | Advancing columns | Unresolved tie | Invalid judge rankings / field-size rules | Material Rules 5–8 difference |
|---|---|---|---|---|---|---|---|
| **Dawson 1963** | Exact text not inspected. Mora treats Dawson as the canonical traditional exposition. | Exact wording not verified. | Exact wording not verified. | Dawson is described as case-based; some extreme cases are not explicit. | Exact terminal language not verified from source copy. | Not established. | **Cannot responsibly perform a line-by-line comparison without the booklet.** Mora's formalization is specifically intended to agree with all cases Dawson actually treats. citeturn22view0 |
| **Anonymous Dawson-based abridgement / ICAD 1981** | Source not inspected. | — | — | — | — | — | Proven to be an abridgement **based on** Dawson, not an independent origin. No material deviation can be supported from available evidence. citeturn24view0 |
| **DTV 1991 _Grundlagen der Turnierleitung_** | Source not inspected. | — | — | Mora reports a disagreement with Dawson in an extreme example. | — | — | **Potential material historical divergence**, but the evidence obtained is insufficient to say that it affects Rules 5–8 specifically. citeturn22view0 |
| **DTV 2001 Majoritätssystem** | Uses the same separate-dance Rules 1–8 in Mora's classification. | Same Rules 1–8. | Same Rules 1–8. | Same Rules 1–8. | Same Rules 1–8. | Not established from source text. | **No single-dance difference identified.** Its material difference is dropping traditional Rules 10–11 in the multi-dance stage. citeturn24view0 |
| **Mora 2001, Traditional System formalization** | Formalizes the cumulative-majority method systematically. | Larger cumulative count is superior. | Count tie proceeds to qualifying-mark sum; subsequent criteria resolve tied groups. | Designed to cover extreme cases omitted by case-based accounts. | Formal treatment preserves ties where criteria cannot divide a group. | Analytical rather than governing source. | Intended to produce the same Rules 1–8 result as traditional Skating while removing procedural ambiguity; Mora states all his Traditional/Simplified/Improved variants agree for each individual dance. citeturn22view0turn24view0 |
| **Current WDSF-linked eleven-rule text** | Majority examples: 3→2, 5→3, 7→4. For place \(t\), count “\(t\)th and higher,” i.e. ranks \(1\ldots t\). citeturn9view0 | **Greater majority wins**, and all competitors that have a majority are placed before competitors that do not. citeturn10view0 | Equal majority: sum only the ranks included in the cumulative range; lower sum wins. citeturn10view2 | Equal count+sum: advance **those tied competitors only**. No majority: advance all still-unplaced competitors. citeturn10view3turn10view4 | Continue to the last possible \(N\)-and-higher column; if still equal, give each tied competitor the mean of the consecutive positions occupied. citeturn10view4 | Judge ties prohibited; every finalist must receive a place; duplicate/illegible mark is returned via Chair to judge for correction. Text also says a final has at most eight competitors. citeturn9view0 | Baseline current technical text. Two obvious textual mistakes identified below do not alter the tables/algorithm. |
| **Svenska Danssportförbundet Version 1, 2024-09-01** | Same as WDSF-linked text. Rules 5–8 at pp. 5–9. citeturn27view0 | Same. | Same. | Same. | Explicitly gives 3½ for a tie occupying third/fourth and 4 for a three-way third/fourth/fifth tie; announcer calls both situations “tied for 3rd.” citeturn28view2 | Same duplicate/illegible correction, judge-no-tie rule and eight-finalist statement. citeturn27view0 | **No material algorithmic difference found.** Dated/branded layout edition; contains the same apparent Rule 6 and Rule 7 textual errors. |
| **Canada DanceSport 2025–2026** | Does not restate Rules 5–8. | Inherited by reference. | Inherited by reference. | Inherited by reference. | Inherited by reference. | Rule 20.05 explicitly sends a marking card with an **error or omission** back to the judge for correction. Rule 20 applies to International Style. citeturn18view1 | **No independent Canadian variant identified**: Rule 20.06 incorporates the WDSF definition dynamically. |
| **WSDC Relative Placement, 2010** | Unique ordinal rankings and majority are explicit; document explains preference for odd panels. citeturn28view3 | Related majority methodology. | Full equivalence to Skating Rule 7 was not established in this audit. | Separate WSDC presentation. | Not established from the inspected page. | Judge may not give the same rank to multiple competitors. | **Related swing system, not evidence of a WDSF Rules 5–8 edition.** Do not silently substitute one standard for the other. |

### What “majority” means

The modern rule text gives examples rather than an algebraic formula: a majority of three judges is two, of five is three, and of seven is four. citeturn27view0 For \(J\) judges, the resulting strict-majority threshold is

\[
M=\left\lfloor\frac{J}{2}\right\rfloor+1.
\]

For your guaranteed odd panel,

\[
M=\frac{J+1}{2}.
\]

The rule does **not** award the place based on the average rank or total rank sum. A qualifying majority count is the primary criterion.

### Meaning of the cumulative columns

For competitor \(c\), define

\[
C_c(t)=\#\{j:r_{cj}\le t\}
\]

and

\[
S_c(t)=\sum_{j:r_{cj}\le t}r_{cj}.
\]

Thus the column called “1–3” or “3rd and higher” is \(C_c(3)\), not merely the number of third-place votes. The corresponding Rule 7 sum is \(S_c(3)\), containing only first-, second-, and third-place marks. The current text explicitly distinguishes **counting** in Rules 5/6 from **adding** the included marks when Rule 7 is needed. citeturn27view0

The ordering of criteria is therefore lexicographic:

1. has a strict majority versus does not;
2. among majority competitors, **larger \(C_c(t)\)**;
3. among equal counts, **smaller \(S_c(t)\)**;
4. if both remain equal, increase \(t\) **for that tied subgroup** and repeat.

A low sum can never defeat a competitor with a greater majority at the same threshold; Rule 6 comes before Rule 7. citeturn27view0

### Rule 7 versus Rule 8 advancement

This distinction is critical to software.

Under **Rule 7**, if A and B have the same qualifying majority and same qualifying sum, **only A and B** advance to the next column. Other competitors are temporarily left out of that tie-resolution branch. When the A/B tie is resolved, the calculation returns to the remaining field at the appropriate reached column. The Rule 7 worked example explicitly does this to competitors 74 and 75. citeturn27view0turn28view2

Under **Rule 8**, if **nobody** has a majority for the position under review, the calculation moves to the next cumulative column for the still-unplaced field until one or more competitors obtain a majority. At that point Rules 6 and 7 apply to the qualifying group. citeturn27view0

Conflating those two operations is one of the easiest ways for software to produce incorrect edge-case results.

### The terminal column

The current text is explicit that Rule 7's tie search does not continue indefinitely. For \(N\) finalists, the last possible column is \(1\!-\!N\). If an equal-majority/equal-sum tied subgroup remains inseparable there, it shares the positions, each receiving the **mean** of the consecutive positions involved. citeturn28view2

At \(t=N\), every valid judge rank is included, so every remaining competitor necessarily has \(C_c(N)=J\). The remaining distinguishing quantity is the complete rank sum \(S_c(N)\). If those sums are also equal inside a tied group, there is no \(N+1\) column: Rule 7's shared-place outcome applies.

That should be distinguished from the teaching document's statement that a final contains no more than eight competitors. The latter is an organizational final-size rule in that publication, **not a mathematical requirement of the cumulative-majority algorithm**. citeturn27view0 An independent event should decide separately whether it wishes to adopt that eight-finalist restriction.

### Invalid, missing, duplicate and tied rankings

The current teaching text says every finalist receives a placement, a judge may not tie competitors, and a duplicated or illegible number is passed through the Chair to the judge for correction. citeturn27view0 Canada's Rule 20.05 strengthens the operational point by explicitly covering **errors or omissions**: the scrutineer refers the card to the judge for correction. citeturn18view1

Accordingly, the best-supported interpretation is that Rules 5–8 operate on a **complete strict ranking**, normally the permutation \(1,\ldots,N\) from each judge. There is no authority in these sources for software to silently invent a missing rank, discard an inconvenient judge, break a judge's tie algorithmically, or convert duplicate placements into averaged ranks.

An out-of-range rank, incomplete permutation, duplicated rank, judge-created tie, or missing finalist should therefore be considered an **input-validity problem before Skating tabulation**, not a new Rule 5–8 case. Exactly how software pauses, flags, or permits a Chair override is an organizer/workflow policy because the rules describe human correction rather than software behavior.

## Worked examples

The following are independent transcriptions and recomputations of the official federation example set. For audit purposes:

* `C=[C1,C2,...,CN]` is the cumulative count vector.
* `S=[S1,S2,...,SN]` is the cumulative qualifying-rank-sum vector.
* The `S` vectors are shown even where the published example never needs them, so they can serve as regression-test data.
* The examples appear in Svenska Danssportförbundet Version 1, 2024-09-01, Rules 5–8 on printed pp. 5–9, and correspond to the worked-example family in the WDSF-linked document. citeturn27view0turn9view0

### Rule 5 example

Five judges; majority \(M=3\). The published ranks and Rule 5 narrative begin on printed p. 5. citeturn27view0

| Competitor | A | B | C | D | E | `C[1..6]` | `S[1..6]` | Final |
|---|---:|---:|---:|---:|---:|---|---|---:|
| 51 | 1 | 1 | 1 | 2 | 1 | `[4,5,5,5,5,5]` | `[4,6,6,6,6,6]` | 1 |
| 52 | 4 | 2 | 2 | 1 | 2 | `[1,4,4,5,5,5]` | `[1,7,7,11,11,11]` | 2 |
| 53 | 3 | 3 | 3 | 5 | 4 | `[0,0,3,4,5,5]` | `[0,0,9,13,18,18]` | 3 |
| 54 | 2 | 4 | 5 | 4 | 3 | `[0,1,2,4,5,5]` | `[0,2,5,13,18,18]` | 4 |
| 55 | 5 | 6 | 4 | 3 | 5 | `[0,0,1,2,4,5]` | `[0,0,3,7,17,23]` | 5 |
| 56 | 6 | 5 | 6 | 6 | 6 | `[0,0,0,0,1,5]` | `[0,0,0,0,5,29]` | 6 |

The placement trace is:

`1–1`: 51 has four votes, so 51 is first.
`1–2`: among the remaining competitors, 52 has four, so 52 is second.
`1–3`: 53 has three, so 53 is third.
`1–4`: 54 has four, so 54 is fourth.
`1–5`: 55 has four, so 55 is fifth.
`1–6`: 56 has five, so 56 is sixth.

No sum comparison is required. This is pure Rule 5 counting. The official prose emphasizes that the marks are **counted rather than added** at this stage. citeturn27view0

### Rule 6 example

Seven judges; majority \(M=4\). Published on printed p. 6. citeturn27view0

| Competitor | A | B | C | D | E | F | G | `C[1..6]` | `S[1..6]` | Final |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| 61 | 1 | 1 | 2 | 1 | 4 | 2 | 1 | `[4,6,6,7,7,7]` | `[4,8,8,12,12,12]` | 1 |
| 62 | 6 | 2 | 1 | 5 | 2 | 1 | 2 | `[2,5,5,5,6,7]` | `[2,8,8,8,13,19]` | 2 |
| 63 | 2 | 4 | 3 | 3 | 6 | 3 | 3 | `[0,1,5,6,6,7]` | `[0,2,14,18,18,24]` | 3 |
| 64 | 3 | 3 | 5 | 2 | 1 | 5 | 4 | `[1,2,4,5,7,7]` | `[1,3,9,13,23,23]` | 4 |
| 65 | 4 | 5 | 6 | 4 | 3 | 6 | 5 | `[0,0,1,3,5,7]` | `[0,0,3,11,21,33]` | 5 |
| 66 | 5 | 6 | 4 | 6 | 5 | 4 | 6 | `[0,0,0,2,4,7]` | `[0,0,0,8,18,36]` | 6 |

Trace:

At `1–1`, competitor 61 has \(C=4\), so is first. At `1–2`, 62 has \(C=5\), so is second. At `1–3`, both 63 and 64 have a majority: 63 has **5**, 64 has **4**. Rule 6's greater-majority criterion therefore orders them third and fourth. citeturn27view0

Now only 65 and 66 remain. At `1–4`, their counts are 3 and 2: neither has the majority of four. Advance to `1–5`; the counts are 5 and 4, respectively. Rule 6 therefore places 65 fifth and 66 sixth.

This exposes the teaching document's apparent typo. Its narrative first says to move from `1–4` to `1–5`, but then describes 65's five marks as “4th place and higher.” The rank matrix proves that 65 has only **three** marks \(\le4\) and **five** marks \(\le5\). The result is internally consistent only if the latter phrase reads “5th place and higher.” citeturn27view0

### Rule 7 example

Seven judges; majority \(M=4\). Published on printed pp. 7–8. citeturn27view0turn28view2

| Competitor | A | B | C | D | E | F | G | `C[1..6]` | `S[1..6]` | Final |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| 71 | 3 | 1 | 6 | 1 | 1 | 2 | 1 | `[4,5,6,6,6,7]` | `[4,6,9,9,9,15]` | 1 |
| 72 | 2 | 2 | 1 | 5 | 3 | 1 | 3 | `[2,4,6,6,7,7]` | `[2,6,12,12,17,17]` | 2 |
| 73 | 1 | 5 | 4 | 2 | 2 | 6 | 2 | `[1,4,4,5,6,7]` | `[1,7,7,11,16,22]` | 3 |
| 74 | 5 | 4 | 2 | 4 | 6 | 5 | 4 | `[0,1,1,4,6,7]` | `[0,2,2,14,24,30]` | 4 |
| 75 | 4 | 6 | 3 | 3 | 5 | 4 | 6 | `[0,0,2,4,5,7]` | `[0,0,6,14,19,31]` | 5 |
| 76 | 6 | 3 | 5 | 6 | 4 | 3 | 5 | `[0,0,2,3,5,7]` | `[0,0,6,10,20,32]` | 6 |

The important sequence is:

At `1–1`, 71 has four firsts and wins.

At `1–2`, both 72 and 73 have \(C=4\). Rule 6 cannot distinguish them, so Rule 7 adds only their qualifying marks:

\[
S_{72}(2)=2+2+1+1=6
\]

\[
S_{73}(2)=1+2+2+2=7.
\]

The lower sum makes 72 second and 73 third. This is the official Rule 7 example of an equal majority resolved by sum. citeturn27view0

For fourth, none of 74, 75 and 76 has a majority at `1–3`. At `1–4`, 74 and 75 each have \(C=4\), and each has \(S=14\). Rule 7 therefore says to advance **those two only** to `1–5`. Their counts become 6 and 5, so Rule 6 now separates them: 74 fourth, 75 fifth. The calculation then returns to 76, which has \(C_{76}(5)=5\) and receives sixth. citeturn27view0turn28view2

The same Rule 7 text also gives the terminal shared-place rule, though not as a complete rank matrix. If two competitors remain tied through the last possible column while occupying positions 3 and 4, the scrutineering result is **3½ each**. If three occupy 3, 4 and 5, the result is **4 each**. For announcement purposes, the document says all are described as tied for the highest position involved—“tied for 3rd” in both examples. citeturn28view2

### Rule 8 example

Seven judges; majority \(M=4\). Rule 8 begins on printed p. 8 and its matrix continues on p. 9. citeturn27view0turn28view2

| Competitor | A | B | C | D | E | F | G | `C[1..6]` | `S[1..6]` | Final |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|
| 81 | 3 | 3 | 3 | 2 | 5 | 2 | 3 | `[0,2,6,6,7,7]` | `[0,4,16,16,21,21]` | 1 |
| 82 | 4 | 4 | 4 | 3 | 2 | 3 | 2 | `[0,2,4,7,7,7]` | `[0,4,10,22,22,22]` | 2 |
| 83 | 2 | 2 | 6 | 6 | 4 | 1 | 4 | `[1,3,3,5,5,7]` | `[1,5,5,13,13,25]` | 3 |
| 84 | 1 | 6 | 1 | 5 | 1 | 4 | 6 | `[3,3,3,4,5,7]` | `[3,3,3,7,12,24]` | 4 |
| 85 | 5 | 5 | 5 | 1 | 3 | 6 | 1 | `[2,2,3,3,6,7]` | `[2,2,5,5,20,26]` | 5 |
| 86 | 6 | 1 | 2 | 4 | 6 | 5 | 5 | `[1,2,2,3,5,7]` | `[1,3,3,7,17,29]` | 6 |

At `1–1`, nobody has four first-place marks. At `1–2`, nobody has four marks in the top two. Rule 8 therefore advances the entire unplaced field to `1–3`. There, competitor 81 has six qualifying marks and 82 has four. Both have a majority; Rule 6 orders the greater majority first, producing first and second. The published narrative states exactly this. citeturn27view0

For the remaining competitors, at `1–4` competitors 83 and 84 have counts five and four, respectively, so they become third and fourth. At `1–5`, the independently recomputed counts for 85 and 86 are six and five, producing fifth and sixth.

The final expected vector is therefore:

```text
81,1
82,2
83,3
84,4
85,5
86,6
```

Across all four examples, my recomputation reproduces the published placements. The Rule 6 wording anomaly does **not** reproduce mathematically, which is why it should be recorded as a textual defect rather than treated as an alternative rule.

## Implementation findings

### The best-supported single-dance algorithm

The following is an implementation-equivalent statement of current Rules 5–8. It is deliberately separated into what the sources explicitly require and what must be inferred to turn manual scrutineering instructions into a precise deterministic specification.

#### Explicitly supported requirements

Let there be \(N\) finalists and \(J\) judges. Before Rules 5–8 are applied, each judge gives each finalist one unique placement; the source prohibits judge ties and requires a placement for every finalist. Duplicate, illegible, erroneous or omitted marks are referred for human correction rather than repaired by the Skating calculation. citeturn27view0turn18view1

With an odd panel, define

\[
M=(J+1)/2.
\]

For each unplaced competitor \(c\) and cumulative threshold \(t\), calculate:

\[
C_c(t)=\#\{r_{cj}\le t\},
\]

and, when required,

\[
S_c(t)=\sum_{r_{cj}\le t}r_{cj}.
\]

The current teaching source establishes the following priority:

| Situation at threshold \(t\) | Required action |
|---|---|
| No unplaced competitor has \(C_c(t)\ge M\) | Increase \(t\); this is Rule 8. citeturn27view0 |
| Exactly one competitor has a majority | Award the next available place to that competitor. |
| Several have a majority, with different \(C_c(t)\) | Larger \(C_c(t)\) ranks first; all majority competitors are handled before non-majority competitors. This is Rule 6. citeturn27view0 |
| Several have the same \(C_c(t)\) | Compare \(S_c(t)\); smaller sum ranks first. This is Rule 7. citeturn27view0 |
| A subgroup has the same \(C_c(t)\) **and** \(S_c(t)\) | Increase \(t\) **for that subgroup only**, then reapply majority/count/sum logic. citeturn28view2 |
| That exact tie survives through \(t=N\) | Give the tied competitors the arithmetic mean of the consecutive placements they collectively occupy. citeturn28view2 |

A compact way to understand Rule 6 and Rule 7 together is that, within a set that has achieved the majority at a particular cumulative column, the current column compares

\[
\big(-C_c(t),\,S_c(t)\big),
\]

with exact ties causing a recursive move to \(t+1\) for the tied subgroup. That tuple notation is my formalization, not wording found in the rulebook, but it reproduces the published examples and stated precedence.

### Placement consumption under a shared tie

If \(k\) competitors remain inseparable and the next available position is \(p\), the source's mean rule implies that all receive

\[
\frac{p+(p+k-1)}{2}
=p+\frac{k-1}{2}.
\]

They nevertheless consume all \(k\) consecutive slots \(p,\ldots,p+k-1\). Consequently, the next non-tied competitor is placed at \(p+k\), not at the numeric value immediately above the shared mean.

Because these are means of consecutive integers, a Skating shared place is always an integer or a half-integer. The official examples use **3½** and **4**. citeturn28view2

For future Rules 9–11 work, do not assume those fractions are always treated simply as floating-point numbers in every comparison. The 2024 full eleven-rule document contains additional instructions for fractional dance placements during multi-dance Rule 10 processing—another reason to keep Rules 9–11 outside the present single-dance module boundary. citeturn27view0

### Invalid ballots should be rejected before tabulation

The rule evidence supports this validity contract for a single-dance final:

\[
\text{each judge's ranks}=\{1,2,\ldots,N\}
\]

exactly once each.

That equation is an implementation interpretation of Rules 2–4 rather than a literal formula in the document, but it follows directly from the requirements that every competitor be placed, rankings progress first/second/third/etc., and judges may not tie competitors. citeturn27view0

The most defensible behavior for an electronic system is therefore to classify these as **ballot errors**, not Skating outcomes:

| Condition | Source position | Defensible software policy |
|---|---|---|
| Missing competitor/rank | Every finalist must be placed; CDS expressly calls omissions correctable. citeturn27view0turn18view1 | Block final calculation pending correction. |
| Duplicate rank | Explicitly identified as an error to be corrected with the judge. citeturn27view0 | Block; never auto-renumber. |
| Judge tie | Explicitly prohibited. citeturn27view0 | Block; send for correction. |
| Illegible value | Explicitly sent to Chair/judge for correction. citeturn27view0 | Electronic equivalent should require an authoritative corrected value. |
| Out-of-range/non-integer value | Not named individually, but incompatible with Rules 2–4. | Treat as an error under organizer-defined validation policy; do not invent meaning. |
| Judge unavailable to correct an invalid card | Not resolved by Rules 5–8. | **Organizer policy required.** |
| Competitor withdrawal/disqualification after marks are submitted | Not resolved by the Rules 5–8 material reviewed. | **Organizer policy required.** |

Silently dropping an invalid judge is particularly dangerous: it changes \(J\), changes the majority \(M\), and can change every result. Nothing in the reviewed Skating sources authorizes that remedy.

### Points that require organizer decisions

For the event described in the question, I would require the organizer to settle these points explicitly before an audit of the scoring engine:

**Governing version.** State whether the event adopts the WDSF-linked Skating document as archived on a fixed date, rather than an indefinitely moving “current Skating System.”

**Discipline scope.** CDS Rule 20's incorporation is expressly for International Style. Swing has its own WSDC relative-placement authority, and this research did not establish a present WRRC Skating mandate. A mixed ballroom/swing/rock-and-roll event needs to say whether one common algorithm is being adopted locally or each discipline retains its sanctioning body's system. citeturn18view1turn28view3

**Final size.** The WDSF-style teaching text says a final has at most eight competitors. citeturn27view0 Do not hard-code \(N\le8\) merely because Rules 5–8 happen to be explained that way unless the event actually adopts that competition-format restriction.

**Ballot correction workflow.** The human rules assume a Chair and judge can correct the card. Software needs a policy for audit logging, authorization, correction after submission, and the exceptional case in which correction is impossible.

**Stored versus announced tie result.** The mathematical scrutineering result may be 3.5/3.5, while the source says both couples are announced as “tied for 3rd.” citeturn28view2 The data model, reports and public display should distinguish those concepts.

**Future even panels.** Your present event always uses an odd number, so there is no immediate ambiguity. The swing RPSS source likewise explains why odd panels are preferable. citeturn28view3 Should the event ever permit an even panel, the organizer should specify that “majority” means a strict \(>50\%\) majority rather than allowing exactly half.

### What should not be encoded as a rule

The apparent Rule 6 “4th and higher” error should **not** be turned into special-case behavior. The table, marks, immediately preceding sentence, result and general Rules 5–8 logic all require `1–5`; the phrase is internally inconsistent. citeturn27view0

Likewise, the Rule 7 reference to competitor #85 in a field numbered 71–76 should not generate any software interpretation. It is a simple source error. citeturn27view0

Most importantly, no special “give up” behavior should occur merely because the cumulative threshold reaches the number of competitors. Rule 7 tells you what to do: evaluate the final possible column, including its sum comparison, and only then award shared places if the relevant group remains exactly tied. citeturn28view2

## Recommended evidence package

For an independently reviewable software repository, I would preserve a small evidence bundle rather than rely on live URLs alone.

| Repository artifact | Exact source to preserve/reference | Why it belongs in the audit package |
|---|---|---|
| `CanadaDanceSport_RuleBook_2025-08-15_V2.pdf` | Current Canada DanceSport PDF: `https://www.dancesport.ca/attachments/File/Rules/2025%20-%202026%20CDS%20Bylaws%20and%20Rule%20Book%20Eng%20with%20changes%20after%20all%20revisions%20August%2015,%202025%20V2.pdf` | Governing-chain evidence. Preserve Rule 20.05–20.06 and Schedule C. The official website presently identifies this as the current 2025/26 rulebook while the document itself says Effective August 15, 2025. citeturn16view0turn18view1 |
| `WDSF_The_Skating_System_<retrieval-date>.pdf` | Official document entry: `https://www.worlddancesport.org/Document/99473179446/The-Skating-System.pdf`; current Box target: `https://dancesport.app.box.com/s/w60qa4644xcfuggvq03ygjo3ksivwo1w` | Primary technical implementation reference selected by the current WDSF Rules page. Record retrieval date because the document itself lacks a useful edition date. citeturn6view0turn7view0 |
| `WDSF_Rules_Page_<date>.pdf` or HTML snapshot | `https://www.worlddancesport.org/Rules` | Proves that WDSF itself currently presents _The Skating System_ as an official competition resource. This provenance evidence is as important as the PDF bytes. citeturn6view0 |
| `SDF_Skating_System_v1_2024-09-01.pdf` | `https://www.danssport.se/media/z3jlnzuj/the-skating-system-slt-2024-09-01.pdf` | Best dated/versioned federation copy found; title page itself says Version 1, 2024-09-01. Useful for reproducing Rules 5–8 page citations and examples even if the WDSF Box object later changes. citeturn28view0 |
| `Mora_The_Skating_System_2ed_2001-07.pdf` | `https://mat.uab.cat/~xmora/escrutini/skating2en.pdf` | Historical genealogy, Dawson/ICAD/DTV/Carlsen bibliography, explanation of 1956 Rule 11, and a systematic Rules 1–8 formalization. It is analysis, not the governing rule. citeturn22view0turn24view0 |
| `BDC_history_snapshot` | `https://www.britishdancecouncil.com/history-of-the-bdc-and-wdc/` | Establishes that the Official Board of Ballroom Dancing is the historical BDC organization rather than relying on secondary naming claims. citeturn29search3 |
| `WSDC_Relative_Placement_2010.pdf` | `https://www.worldsdc.com/wp-content/uploads/2016/04/Relative_placement.pdf` | Keeps the swing rule lineage separate from the ballroom/WDSF one and prevents accidental assertion that all “relative placement” documents are the same governing source. citeturn28view3 |
| `rules5_8_examples.csv` | The four matrices transcribed above | Creates executable evidence independent of document layout/OCR. Include raw judge marks, \(C_t\), \(S_t\), expected final place, and exact page citation. |
| `PROVENANCE.md` | Repository-maintained | Record what is established, what is inferred, retrieval dates, SHA-256 hashes of each locally archived PDF, and known textual errors such as Rule 6's “4th”/“5th” defect. |
| `HISTORICAL_SOURCES.md` | Bibliographic records for Dawson 1963, ICAD 1981, DTV 1991, Carlsen 1996, Grassby 2001 | These works should be cited as “not directly inspected” until actual copies are obtained. This prevents secondary bibliography from silently becoming asserted primary evidence. |

For every binary PDF actually committed or retained internally, the audit file should record **SHA-256, byte size, retrieval date, retrieval URL, document-internal date/version, and the page numbers used by tests**. In particular, preserving a hash of the current WDSF object solves a serious reproducibility problem created by Canada DanceSport's “from time to time” reference: a reviewer years later can determine exactly which WDSF content governed the implementation audit even if WDSF replaces the file at the same URL. citeturn18view1

The machine-test evidence should include, at minimum, the four official examples above plus synthetic cases designed solely to exercise explicit terminal behavior: two competitors equal through column \(N\), three competitors equal through \(N\), a Rule 7 subgroup that resolves several columns later, and a Rule 8 case with no majority until a late threshold. Those synthetic tests should be labeled as **derived tests**, not official examples.

The repository should also preserve the distinction between **source fact** and **calculated expected value**. For example, the published Rule 6 marks are source facts; `C65(4)=3` and `C65(5)=5` are independently reproducible calculations; the conclusion that “4th” is erroneous follows from those facts. That evidentiary separation makes future review far more robust than simply copying the published result column.

## Unresolved questions

| Question not established | Why it remains unresolved | Best next research step |
|---|---|---|
| **Was the original ballroom majority principle formally adopted in 1937 or first used in 1938?** | The accessible sources conflict: the common secondary history says 1937; Mora says the majority criterion entered ballroom competition at the 1938 Star Championships. No contemporaneous Official Board document was located. citeturn29search1turn22view0 | Examine 1937–1939 **Official Board of Ballroom Dancing minutes/circulars**, contemporaneous _Dancing Times_, Star Championships programmes/results, and Blackpool archival material. BDC and the British Library are the strongest institutional targets. |
| **What exactly does the title/copyright page of Dawson 1963 say?** | The work's existence, author, year and broad issuing body are well supported through Mora, but later bibliographies disagree about imprint details, and no primary scan was obtained. citeturn24view0turn25search5 | Obtain a physical/library copy from the British Library, BDC, ISTD or a specialist dance archive; photograph title, verso, contents and the pages containing Rules 5–8. |
| **Did Dawson 1963 number and phrase Rules 5–8 exactly like the modern teaching PDF?** | Mora says his formulation agrees with Dawson's considered cases but also says Dawson's case-oriented account leaves extreme cases unstated. That is not enough for a textual equivalence claim. citeturn22view0 | Compare Dawson pages directly against current WDSF and 1981 ICAD texts, preferably with a line-level diff/transcription. |
| **What exactly was the 1981 ICAD _Skating System_?** | Mora establishes that it reproduced an anonymous Dawson-based abridgement, but the actual document was not obtained. citeturn24view0 | Request WDSF historical archives or national-member libraries for the 1981 ICAD publication; establish title page, page count and text. |
| **Is the current WDSF eleven-rule worked-example PDF descended from that 1981 anonymous abridgement, Jim Warren's later exposition, or another source?** | WDSF currently endorses the document, but the accessible PDF family is unattributed. Textual dissemination alone cannot establish original authorship. citeturn6view0turn9view0 | Ask WDSF for the source file's author, creation/revision history and predecessor; examine WDSF/IDSF web archives and document metadata; then collate against the 1981, 1994 and 2000 texts. |
| **When was the current WDSF PDF first officially published?** | It is undated. A present-day WDSF URL establishes current status, not original publication date. | Locate dated WDSF/IDSF archived Rules pages and old document repositories. A verified earliest Wayback capture would establish a _terminus ante quem_ but still should not automatically be called the publication date. |
| **What is the exact DTV 1991 disagreement with Dawson, and does it affect Rules 5–8?** | Mora says the two disagree in an extreme example but the DTV book itself was not obtained. citeturn22view0 | Obtain _Grundlagen der Turnierleitung_, 2nd ed., especially appendix pp. 10–24 and Example 15, and reproduce both calculations beside Dawson Example N. |
| **What text did the NDCA-endorsed Canadian publication _Certified Correct_ use for Rules 5–8?** | Mora establishes Jeff Carlsen, Halifax, 1996 and NDCA endorsement, but no inspectable copy was found. citeturn24view0 | Locate the book through Canadian library catalogues, NDCA archives or used specialist collections. This is particularly worthwhile for a Canadian software audit. |
| **Are there DanseSport Québec-specific additions or exceptions?** | This investigation established the current Canada DanceSport/WDSF chain but did not inspect a current Québec-specific scrutineering rule that could modify it. Canada DanceSport identifies Québec as one of its regional member organizations. citeturn14view0 | Obtain the current DanseSport Québec competition regulations and sanction conditions and check expressly for scoring, finalist-count or adjudication provisions. |
| **Does WRRC currently use traditional Skating Rules 5–8 in any rock-and-roll discipline?** | No sufficiently authoritative WRRC document establishing that proposition was located in the material retrieved. It would be unsafe to infer it merely because Skating is common in other judged dance sports. | Search current and archived **World Rock'n'Roll Confederation** sporting/judging regulations by discipline and contact its judging/sporting commission if historical versions are absent online. |
| **Is WSDC Relative Placement algorithmically identical to ballroom Rules 5–8 in every terminal tie case?** | The official WSDC source clearly shares unique ordinal ranks, majority logic and an odd-panel preference, but this audit did not establish complete rule-by-rule equivalence. citeturn28view3 | Transcribe all WSDC RPSS pages and construct the same formal \(C_t,S_t\) comparison used above before claiming equivalence. |
| **Is the WDSF Box object byte-identical to the accessible 22-page mirror?** | WDSF's official redirect was verified, and the mirror reproduces the expected title/rules, but a cryptographic comparison of the two objects was not obtained. citeturn7view0turn9view0 | Download both exact binaries from a normal browser/session, record SHA-256, metadata and page count, and retain the result in `PROVENANCE.md`. |

The most consequential unresolved historical issue is the Dawson/ICAD textual chain; the most consequential **implementation** issue is much simpler: the current Canadian rulebook points to WDSF, WDSF currently points to the eleven-rule _The Skating System_, and the detailed Rules 5–8 in that current textual family are internally consistent enough to define a reproducible algorithm once its two obvious teaching-text errors are treated as errors rather than alternate rules. citeturn18view1turn6view0turn27view0
