using UnityEngine;
using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// Event card resolution — per-card handler dispatch.
    /// Mirrors the Python engine/events.py event handler registry.
    /// </summary>
    public class EventResolver
    {
        private readonly GameManager game;
        private readonly EffectResolver effects;

        // Delegate type for event handlers
        public delegate List<string> EventHandler(
            PlayerManager playerState, PlayerManager enemyState,
            string player, string enemy);

        private Dictionary<string, EventHandler> handlers;

        public EventResolver(GameManager game, EffectResolver effects)
        {
            this.game = game;
            this.effects = effects;
            BuildRegistry();
        }

        /// <summary>
        /// Resolve an event card. Returns list of result messages.
        /// </summary>
        public List<string> ResolveEvent(CardData card, string player)
        {
            PlayerManager pState = game.GetPlayerState(player);
            PlayerManager eState = game.GetEnemyPlayer(player);
            string enemy = player == "fp" ? "shadow" : "fp";

            if (handlers.TryGetValue(card.cardName, out var handler))
                return handler(pState, eState, player, enemy);

            // Fallback for unimplemented events
            return new List<string>
            {
                $"{card.cardName} resolves! (Effects not yet implemented.)"
            };
        }

        // --- Registry ---

        private void BuildRegistry()
        {
            handlers = new Dictionary<string, EventHandler>
            {
                // Gondor
                ["For Gondor!"] = ForGondor,
                ["The Beacons Are Lit"] = BeaconsAreLit,
                ["The Last Debate"] = LastDebate,

                // Mordor
                ["The Shadow Spreads"] = ShadowSpreads,
                ["Shadow's Reach"] = ShadowsReach,
                ["The Lidless Eye"] = LidlessEye,
                ["The Fires of Mount Doom"] = FiresOfMountDoom,

                // Elven
                ["Lembas"] = Lembas,
                ["The Last Alliance"] = LastAlliance,
                ["The Light of the Evenstar"] = LightOfTheEvenstar,

                // Dwarven
                ["To Me! O My Kinsfolk!"] = ToMeOKinsfolk,
                ["The Ire of the Mountain"] = IreOfTheMountain,
                ["The Hammer Falls"] = HammerFalls,

                // Rohan
                ["Ride of the Rohirrim"] = RideOfTheRohirrim,
                ["Muster the Rohirrim"] = MusterTheRohirrim,
                ["Forth Eorlingas!"] = ForthEorlingas,

                // Hobbit
                ["The Straight Road"] = StraightRoad,
                ["I Will Not Say the Day Is Done"] = IWillNotSay,

                // Isengard
                ["The White Hand"] = WhiteHand,
                ["Isengard Unleashed"] = IsengardUnleashed,
                ["A New Power Rises"] = NewPowerRises,

                // Moria
                ["Drums in the Deep"] = DrumsInTheDeep,
                ["They Are Coming"] = TheyAreComing,
            };
        }

        // ================================================================
        // Gondor
        // ================================================================

        private List<string> ForGondor(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            int count = 0;
            foreach (var loc in game.board.locations)
            {
                foreach (var ally in loc.GetAllies(player))
                {
                    ally.tempToughnessBonus += 2;
                    count++;
                }
            }
            msgs.Add($"For Gondor! {count} allies gain +2 Toughness this turn.");
            return msgs;
        }

        private List<string> BeaconsAreLit(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            int searchCount = System.Math.Min(5, ps.deck.Count);
            CardData found = null;
            var searched = new List<CardData>();

            for (int i = 0; i < searchCount; i++)
            {
                CardData c = ps.deck[ps.deck.Count - 1];
                ps.deck.RemoveAt(ps.deck.Count - 1);
                if (found == null && c.cardType == CardType.Ally &&
                    c.faction == Faction.Gondor)
                {
                    found = c;
                }
                else
                {
                    searched.Add(c);
                }
            }

            if (found != null)
            {
                ps.hand.Add(found);
                msgs.Add($"Found {found.cardName}! Added to hand.");
            }

            // Put the rest back
            ps.deck.AddRange(searched);
            ps.ShuffleDeck();
            msgs.Add($"Searched {searchCount} cards.");
            return msgs;
        }

        private List<string> LastDebate(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            int searchCount = System.Math.Min(7, ps.deck.Count);
            CardData bestCard = null;
            var rest = new List<CardData>();

            for (int i = 0; i < searchCount; i++)
            {
                CardData c = ps.deck[ps.deck.Count - 1];
                ps.deck.RemoveAt(ps.deck.Count - 1);
                if (bestCard == null)
                    bestCard = c;
                else
                    rest.Add(c);
            }

            if (bestCard != null)
            {
                ps.hand.Add(bestCard);
                msgs.Add($"The Last Debate: Chose {bestCard.cardName}. Added to hand.");
            }

            // Rest go to bottom
            rest.AddRange(ps.deck);
            ps.deck = rest;
            msgs.Add($"Put {rest.Count - ps.deck.Count} cards on bottom of deck.");
            return msgs;
        }

        // ================================================================
        // Mordor
        // ================================================================

        private List<string> ShadowSpreads(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            game.ring.AddCorruption(1);
            msgs.Add($"Shadow Spreads: +1 Corruption (now {game.ring.corruption}/30).");

            foreach (var loc in game.board.locations)
            {
                if (loc.controller == player || loc.IsContested)
                {
                    var token = ScriptableObject.CreateInstance<CardData>();
                    TokenFactory.ConfigureOrcToken(token);
                    var tokenAlly = new BoardAlly
                    {
                        card = token,
                        currentToughness = token.toughness,
                        turnEntered = ps.turnNumber,
                    };
                    loc.AddAlly(tokenAlly, player, "front");
                    string locName = loc.locationCard != null
                        ? loc.locationCard.cardName : "Open Field";
                    msgs.Add($"Created Orc Token at {locName}.");
                    break;
                }
            }
            return msgs;
        }

        private List<string> ShadowsReach(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            es.DealInfluenceDamage(2);
            game.ring.AddCorruption(1);
            msgs.Add($"Shadow's Reach: 2 Burn damage to " +
                $"{(enemy == "fp" ? "Free Peoples" : "Shadow")} Influence!");
            msgs.Add($"+1 Corruption (now {game.ring.corruption}/30).");
            return msgs;
        }

        private List<string> LidlessEye(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            game.ring.AddCorruption(1);
            msgs.Add($"Lidless Eye: +1 Corruption (now {game.ring.corruption}/30).");

            if (es.hand.Count > 0)
            {
                int lastIdx = es.hand.Count - 1;
                CardData discarded = es.hand[lastIdx];
                es.hand.RemoveAt(lastIdx);
                es.discard.Add(discarded);
                msgs.Add($"Opponent discards {discarded.cardName}.");
            }
            return msgs;
        }

        private List<string> FiresOfMountDoom(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            game.ring.AddCorruption(2);
            foreach (var loc in game.board.locations)
            {
                foreach (var ally in loc.GetAllies(enemy))
                    ally.TakeDamage(3);
            }
            msgs.Add("Fires of Mount Doom: 3 damage to all enemies! +2 Corruption.");
            return msgs;
        }

        // ================================================================
        // Elven
        // ================================================================

        private List<string> Lembas(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            var hero = ps.hero;
            if (hero != null && hero.currentToughness < hero.card.toughness)
            {
                hero.Heal(3);
                msgs.Add($"Lembas: Healed 3 damage from {hero.card.cardName} (+1 Power this turn).");
            }
            else
            {
                msgs.Add("Lembas: No damage to heal. (+1 Power still gained.)");
            }
            return msgs;
        }

        private List<string> LastAlliance(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            int searchCount = System.Math.Min(8, ps.deck.Count);
            CardData found = null;
            var rest = new List<CardData>();

            for (int i = 0; i < searchCount; i++)
            {
                CardData c = ps.deck[ps.deck.Count - 1];
                ps.deck.RemoveAt(ps.deck.Count - 1);
                if (found == null && c.cardType == CardType.Ally &&
                    c.creatureTypes != null &&
                    (c.creatureTypes.Contains("Elf") || c.creatureTypes.Contains("Man")))
                {
                    found = c;
                }
                else
                {
                    rest.Add(c);
                }
            }

            rest.AddRange(ps.deck);
            ps.deck = rest;

            if (found != null)
            {
                var ally = new BoardAlly
                {
                    card = found,
                    currentToughness = found.toughness,
                    turnEntered = ps.turnNumber,
                };
                bool placed = false;
                foreach (var loc in game.board.locations)
                {
                    if (loc.controller == player || loc.IsContested)
                    {
                        loc.AddAlly(ally, player, "front");
                        msgs.Add($"The Last Alliance: Deployed {found.cardName} to location!");
                        placed = true;
                        break;
                    }
                }
                if (!placed)
                {
                    game.board.DeployAlly(ally, player);
                    msgs.Add($"The Last Alliance: Deployed {found.cardName} to deployment zone.");
                }
            }
            else
            {
                msgs.Add($"The Last Alliance: No Elf or Man ally in top {searchCount}.");
            }
            return msgs;
        }

        private List<string> LightOfTheEvenstar(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            BoardAlly target = null;

            if (ps.hero != null && ps.hero.IsAlive)
            {
                target = ps.hero;
            }
            else
            {
                var allAllies = game.board.GetAllAllies(player);
                foreach (var a in allAllies)
                {
                    if (target == null || a.card.power > target.card.power)
                        target = a;
                }
            }

            if (target != null)
            {
                target.tempPowerBonus += 1;
                target.tempToughnessBonus += 1;
                msgs.Add($"Light of the Evenstar: {target.card.cardName} gains Stealth and +1/+1 this turn.");
            }
            else
            {
                msgs.Add("Light of the Evenstar: No valid target.");
            }
            return msgs;
        }

        // ================================================================
        // Dwarven
        // ================================================================

        private List<string> ToMeOKinsfolk(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            int searchCount = System.Math.Min(5, ps.deck.Count);
            CardData found = null;
            var rest = new List<CardData>();

            for (int i = 0; i < searchCount; i++)
            {
                CardData c = ps.deck[ps.deck.Count - 1];
                ps.deck.RemoveAt(ps.deck.Count - 1);
                if (found == null && c.cardType == CardType.Ally &&
                    c.creatureTypes != null && c.creatureTypes.Contains("Dwarf"))
                {
                    found = c;
                }
                else
                {
                    rest.Add(c);
                }
            }

            if (found != null)
            {
                ps.hand.Add(found);
                msgs.Add($"To Me! O My Kinsfolk!: Found {found.cardName}! Added to hand.");
            }
            else
            {
                msgs.Add("To Me! O My Kinsfolk!: No Dwarf ally in top 5.");
            }

            rest.AddRange(ps.deck);
            ps.deck = rest;
            return msgs;
        }

        private List<string> IreOfTheMountain(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            bool destroyed = false;

            foreach (var loc in game.board.locations)
            {
                // Destroy enemy-controlled location
                if (loc.controller == enemy && loc.locationCard != null && loc.currentDefense > 0)
                {
                    string locName = loc.locationCard.cardName;
                    loc.locationCard = null;
                    loc.currentDefense = 0;
                    loc.controller = null;
                    loc.fortifyBonus = 0;
                    msgs.Add($"The Ire of the Mountain: Destroyed {locName}!");
                    destroyed = true;
                    break;
                }

                // Destroy an enemy artifact
                foreach (var ally in loc.GetAllies(enemy))
                {
                    if (ally.artifacts.Count > 0)
                    {
                        CardData art = ally.artifacts[0];
                        ally.artifacts.RemoveAt(0);
                        es.discard.Add(art);
                        msgs.Add($"The Ire of the Mountain: Destroyed {art.cardName}!");
                        destroyed = true;
                        break;
                    }
                }
                if (destroyed) break;
            }

            if (!destroyed)
                msgs.Add("The Ire of the Mountain: No enemy Artifact or Location to destroy.");

            // Bonus: controlling a Dwarf draws 2 cards
            bool hasDwarf = false;
            foreach (var loc in game.board.locations)
            {
                foreach (var ally in loc.GetAllies(player))
                {
                    if (ally.card.creatureTypes != null &&
                        ally.card.creatureTypes.Contains("Dwarf"))
                    {
                        hasDwarf = true;
                        break;
                    }
                }
                if (hasDwarf) break;
            }
            if (hasDwarf)
            {
                var drawn = ps.DrawCards(2);
                msgs.Add($"Controlling a Dwarf: Drew {drawn.Count} cards.");
            }

            return msgs;
        }

        private List<string> HammerFalls(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            LocationSlot targetLoc = game.board.GetLocation(1);
            if (targetLoc != null)
            {
                foreach (var ally in targetLoc.GetAllies(enemy))
                    ally.TakeDamage(4);
            }
            msgs.Add("The Hammer Falls: 4 damage to enemies at center location!");
            return msgs;
        }

        // ================================================================
        // Rohan
        // ================================================================

        private List<string> RideOfTheRohirrim(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            BoardAlly target = null;

            foreach (var loc in game.board.locations)
            {
                foreach (var ally in loc.GetAllies(player))
                {
                    if (ally.card.faction == Faction.Rohan ||
                        (ally.card.creatureTypes != null &&
                         ally.card.creatureTypes.Contains("Rider")))
                    {
                        if (target == null || ally.card.power > target.card.power)
                            target = ally;
                    }
                }
            }

            if (ps.hero != null && ps.hero.card.faction == Faction.Rohan &&
                ps.hero.IsAlive &&
                (target == null || ps.hero.card.power > target.card.power))
            {
                target = ps.hero;
            }

            if (target != null)
            {
                bool alreadyCharge = target.HasCharge;
                int bonus = alreadyCharge ? 3 : 2;
                target.tempPowerBonus += bonus;
                msgs.Add($"Ride of the Rohirrim: {target.card.cardName} gains Charge and +{bonus} Power!");
            }
            else
            {
                msgs.Add("Ride of the Rohirrim: No Rohan ally to target.");
            }
            return msgs;
        }

        private List<string> MusterTheRohirrim(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            var controlledLocs = new List<LocationSlot>();
            foreach (var loc in game.board.locations)
            {
                if (loc.controller == player && !loc.IsEmpty)
                    controlledLocs.Add(loc);
            }

            int deployed = 0;
            for (int i = 0; i < 3; i++)
            {
                var riderCard = ScriptableObject.CreateInstance<CardData>();
                TokenFactory.ConfigureRiderToken(riderCard);
                var rider = new BoardAlly
                {
                    card = riderCard,
                    currentToughness = riderCard.toughness,
                    turnEntered = ps.turnNumber,
                    tapped = false,
                };

                if (controlledLocs.Count > 0)
                {
                    LocationSlot targetLoc = controlledLocs[i % controlledLocs.Count];
                    targetLoc.AddAlly(rider, player, "front");
                    deployed++;
                }
                else
                {
                    game.board.DeployAlly(rider, player);
                }
            }
            msgs.Add($"Muster the Rohirrim: Created 3 Rider tokens (2/1 Charge)! " +
                $"{deployed} deployed to locations.");
            return msgs;
        }

        private List<string> ForthEorlingas(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            var rohanAllies = new List<BoardAlly>();

            foreach (var loc in game.board.locations)
            {
                foreach (var ally in loc.GetAllies(player))
                {
                    if (ally.card.faction == Faction.Rohan ||
                        (ally.card.creatureTypes != null &&
                         ally.card.creatureTypes.Contains("Rider")))
                    {
                        rohanAllies.Add(ally);
                    }
                }
            }

            // Sort by power descending
            rohanAllies.Sort((a, b) => b.card.power.CompareTo(a.card.power));

            int buffCount = System.Math.Min(3, rohanAllies.Count);
            for (int i = 0; i < buffCount; i++)
            {
                var ally = rohanAllies[i];
                ally.tempPowerBonus += 2;
                ally.TakeDamage(1);
            }

            msgs.Add($"Forth Eorlingas! {buffCount} Rohan allies gain Charge and +2 Power (take 1 damage)!");
            return msgs;
        }

        // ================================================================
        // Hobbit
        // ================================================================

        private List<string> StraightRoad(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            BoardAlly target = null;

            if (ps.hero != null && ps.hero.IsAlive)
            {
                target = ps.hero;
            }
            else
            {
                var allAllies = game.board.GetAllAllies(player);
                foreach (var a in allAllies)
                {
                    if (target == null || a.card.power > target.card.power)
                        target = a;
                }
            }

            if (target != null)
            {
                msgs.Add($"The Straight Road: {target.card.cardName} gains Stealth this turn.");
                ps.DrawCard();
                msgs.Add("Drew a card — may it survive the journey.");
            }
            else
            {
                msgs.Add("The Straight Road: No valid target.");
            }
            return msgs;
        }

        private List<string> IWillNotSay(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            int removed = System.Math.Min(3, game.ring.corruption);
            for (int i = 0; i < removed; i++)
            {
                if (game.ring.corruption > 0)
                    game.ring.corruption--;
            }
            var drawn = ps.DrawCards(removed);
            msgs.Add($"I Will Not Say: Removed {removed} Corruption! Drew {drawn.Count} cards.");
            return msgs;
        }

        // ================================================================
        // Isengard
        // ================================================================

        private List<string> WhiteHand(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            BoardAlly target = null;
            LocationSlot targetLoc = null;

            foreach (var loc in game.board.locations)
            {
                foreach (var ally in loc.GetAllies(player))
                {
                    if (ally.card.creatureTypes != null &&
                        ally.card.creatureTypes.Contains("Uruk-hai"))
                    {
                        if (target == null || ally.card.power > target.card.power)
                        {
                            target = ally;
                            targetLoc = loc;
                        }
                    }
                }
            }

            if (target != null)
            {
                target.tempPowerBonus += 2;
                target.tempToughnessBonus += 2;
                msgs.Add($"The White Hand: {target.card.cardName} gains +2/+2!");

                if (targetLoc != null && targetLoc.IsContested)
                {
                    bool artDestroyed = false;
                    foreach (var enemyAlly in targetLoc.GetAllies(enemy))
                    {
                        if (enemyAlly.artifacts.Count > 0)
                        {
                            CardData art = enemyAlly.artifacts[0];
                            enemyAlly.artifacts.RemoveAt(0);
                            es.discard.Add(art);
                            msgs.Add($"The White Hand: Destroyed {art.cardName} at contested location!");
                            artDestroyed = true;
                            break;
                        }
                    }
                    if (!artDestroyed)
                        msgs.Add("The White Hand: Contested, but no enemy Artifact to destroy.");
                }
            }
            else
            {
                msgs.Add("The White Hand: No Uruk-hai ally to target.");
            }
            return msgs;
        }

        private List<string> IsengardUnleashed(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            int revealCount = System.Math.Min(6, ps.deck.Count);
            var putInPlay = new List<CardData>();
            var rest = new List<CardData>();

            for (int i = 0; i < revealCount; i++)
            {
                CardData c = ps.deck[ps.deck.Count - 1];
                ps.deck.RemoveAt(ps.deck.Count - 1);
                if (c.cardType == CardType.Ally &&
                    c.creatureTypes != null && c.creatureTypes.Contains("Uruk-hai"))
                {
                    putInPlay.Add(c);
                }
                else
                {
                    rest.Add(c);
                }
            }

            foreach (var c in putInPlay)
            {
                var ally = new BoardAlly
                {
                    card = c,
                    currentToughness = c.toughness,
                    turnEntered = ps.turnNumber,
                    tapped = false,
                };

                int targetLocIdx = -1;
                for (int i = 0; i < game.board.locations.Count; i++)
                {
                    var loc = game.board.locations[i];
                    if (loc.controller == player || loc.IsContested)
                    {
                        targetLocIdx = i;
                        break;
                    }
                }

                if (targetLocIdx >= 0)
                    game.board.GetLocation(targetLocIdx).AddAlly(ally, player, "front");
                else
                    game.board.DeployAlly(ally, player);
            }

            rest.AddRange(ps.deck);
            ps.deck = rest;
            msgs.Add($"Isengard Unleashed: Revealed {revealCount}, put {putInPlay.Count} Uruk-hai into play!");
            return msgs;
        }

        private List<string> NewPowerRises(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            LocationSlot targetLoc = null;
            int bestScore = -1;

            foreach (var loc in game.board.locations)
            {
                int score = loc.GetAllies(player).Count + loc.GetAllies(enemy).Count;
                if (score > bestScore)
                {
                    bestScore = score;
                    targetLoc = loc;
                }
            }

            if (targetLoc == null)
                targetLoc = game.board.GetLocation(1);

            int artifactsDestroyed = 0;
            foreach (string pid in new[] { "fp", "shadow" })
            {
                foreach (var ally in targetLoc.GetAllies(pid))
                {
                    while (ally.artifacts.Count > 0)
                    {
                        CardData art = ally.artifacts[ally.artifacts.Count - 1];
                        ally.artifacts.RemoveAt(ally.artifacts.Count - 1);
                        artifactsDestroyed++;
                        if (pid == "fp")
                            game.fpPlayer.discard.Add(art);
                        else
                            game.shadowPlayer.discard.Add(art);
                    }
                }
            }

            for (int i = 0; i < artifactsDestroyed; i++)
            {
                var tokenCard = ScriptableObject.CreateInstance<CardData>();
                TokenFactory.ConfigureUrukHaiToken(tokenCard);
                var token = new BoardAlly
                {
                    card = tokenCard,
                    currentToughness = tokenCard.toughness,
                    turnEntered = ps.turnNumber,
                };
                targetLoc.AddAlly(token, player, "front");
            }

            msgs.Add($"A New Power Rises: Destroyed {artifactsDestroyed} artifacts, " +
                $"created {artifactsDestroyed} 3/3 Uruk-hai tokens!");
            return msgs;
        }

        // ================================================================
        // Moria
        // ================================================================

        private List<string> DrumsInTheDeep(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            int returned = 0;
            var grab = new List<CardData>();

            foreach (var c in ps.discard)
            {
                if (c.creatureTypes != null && c.creatureTypes.Contains("Goblin") &&
                    returned < 2)
                {
                    grab.Add(c);
                    returned++;
                }
            }

            foreach (var c in grab)
            {
                ps.discard.Remove(c);
                ps.hand.Add(c);
            }

            var tokenCard = ScriptableObject.CreateInstance<CardData>();
            TokenFactory.ConfigureGoblinToken(tokenCard);
            var token = new BoardAlly
            {
                card = tokenCard,
                currentToughness = tokenCard.toughness,
                turnEntered = ps.turnNumber,
            };

            bool placed = false;
            foreach (var loc in game.board.locations)
            {
                if (loc.controller == player || loc.IsContested)
                {
                    loc.AddAlly(token, player, "front");
                    placed = true;
                    break;
                }
            }
            if (!placed)
                game.board.DeployAlly(token, player);

            msgs.Add($"Drums in the Deep: Returned {returned} Goblins from discard + created Goblin token!");
            return msgs;
        }

        private List<string> TheyAreComing(PlayerManager ps, PlayerManager es,
            string player, string enemy)
        {
            var msgs = new List<string>();
            var goblins = new List<CardData>();

            foreach (var c in ps.hand)
            {
                if (c.creatureTypes != null && c.creatureTypes.Contains("Goblin") &&
                    goblins.Count < 3)
                {
                    goblins.Add(c);
                }
            }

            foreach (var c in goblins)
            {
                ps.hand.Remove(c);
                var ally = new BoardAlly
                {
                    card = c,
                    currentToughness = c.toughness,
                    turnEntered = ps.turnNumber,
                    tapped = false,
                };

                bool placed = false;
                foreach (var loc in game.board.locations)
                {
                    if (loc.IsContested || loc.controller == enemy)
                    {
                        loc.AddAlly(ally, player, "front");
                        placed = true;
                        break;
                    }
                }
                if (!placed)
                    game.board.DeployAlly(ally, player);
            }

            msgs.Add($"They Are Coming: Deployed {goblins.Count} Goblins into play!");
            return msgs;
        }
    }
}
