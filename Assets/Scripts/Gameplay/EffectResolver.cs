using UnityEngine;
using System.Collections.Generic;
using LOTRCardGame.Data;

namespace LOTRCardGame.Gameplay
{
    /// <summary>
    /// Handles card ability resolutions: on-enter effects, on-destroy effects,
    /// hero activated abilities, and Ring activation effects.
    /// Mirrors the Python engine/effects.py EffectResolver class.
    /// </summary>
    public class EffectResolver
    {
        private readonly GameManager game;

        public EffectResolver(GameManager game)
        {
            this.game = game;
        }

        // --- On-Enter Effects ---

        /// <summary>
        /// Resolve "When this ally enters play" effects.
        /// Called after an ally is deployed or placed at a location.
        /// </summary>
        public List<string> ResolveOnEnter(BoardAlly ally, string player)
        {
            var msgs = new List<string>();
            CardData card = ally.card;

            // --- Keyword-driven effects ---

            // Swarm: create a token at the ally's location
            if (card.keywords != null && card.keywords.Contains("Swarm"))
            {
                int? locIndex = game.board.FindAllyLocation(ally, player);
                if (locIndex != null && locIndex >= 0)
                {
                    var token = ScriptableObject.CreateInstance<CardData>();
                    TokenFactory.ConfigureOrcToken(token);
                    var tokenAlly = new BoardAlly
                    {
                        card = token,
                        currentToughness = token.toughness,
                        turnEntered = game.GetPlayerState(player).turnNumber,
                    };
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    loc.AddAlly(tokenAlly, player, "front");
                    msgs.Add($"Swarm: Created {token.cardName}!");
                }
            }

            // Fortify: +1 defense to location
            if (card.keywords != null && card.keywords.Contains("Fortify"))
            {
                int? locIndex = game.board.FindAllyLocation(ally, player);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    if (loc.locationCard != null)
                    {
                        loc.fortifyBonus++;
                        loc.currentDefense++;
                        msgs.Add($"Fortify: {loc.locationCard.cardName} gains +1 Defense!");
                    }
                }
            }

            // Scout / Foresight: peek at top of deck
            if (card.keywords != null && card.keywords.Contains("Scout"))
            {
                PlayerManager pState = game.GetPlayerState(player);
                if (pState.deck.Count > 0)
                {
                    CardData top = pState.deck[pState.deck.Count - 1];
                    msgs.Add($"Scout: Top card is {top.cardName}. Keeping on top.");
                }
            }

            if (card.keywords != null && card.keywords.Contains("Foresight"))
            {
                msgs.Add("Foresight: Glimpsed the future. (Simplified)");
            }

            // --- Card-specific on-enter effects ---

            // Watchman of Minas Tirith: Vigilant (+1 Defense)
            if (card.cardName == "Watchman of Minas Tirith")
            {
                int? locIndex = game.board.FindAllyLocation(ally, player);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    if (loc.locationCard != null)
                    {
                        loc.fortifyBonus++;
                        loc.currentDefense++;
                        msgs.Add($"Vigilant: {loc.locationCard.cardName} gains +1 Defense!");
                    }
                }
            }

            // Orc War-band: Swarm
            if (card.cardName == "Orc War-band")
            {
                int? locIndex = game.board.FindAllyLocation(ally, player);
                if (locIndex != null && locIndex >= 0)
                {
                    var token = ScriptableObject.CreateInstance<CardData>();
                    TokenFactory.ConfigureOrcToken(token);
                    var tokenAlly = new BoardAlly
                    {
                        card = token,
                        currentToughness = token.toughness,
                        turnEntered = game.GetPlayerState(player).turnNumber,
                    };
                    game.board.GetLocation(locIndex.Value).AddAlly(tokenAlly, player, "front");
                    msgs.Add($"Swarm: Created {token.cardName}!");
                }
            }

            // Grishnakh: Insurrection
            if (card.cardName == "Grishnákh, Orc-Captain")
                msgs.Add("Insurrection: Orc allies gain +1 Power this turn!");

            // Imrahil: Rally (heal 1 damage from Gondor allies)
            if (card.cardName == "Imrahil, Prince of Dol Amroth")
            {
                int healed = 0;
                foreach (var loc in game.board.locations)
                {
                    foreach (var a in loc.GetAllies(player))
                    {
                        if (a != ally && a.currentToughness < a.card.toughness)
                        {
                            a.Heal(1);
                            healed++;
                        }
                    }
                }
                if (healed > 0)
                    msgs.Add($"Rally: Healed 1 damage from {healed} Gondor allies!");
            }

            // The Great Beast of Gorgoroth: deal 2 damage to enemy allies at location
            if (card.cardName == "The Great Beast of Gorgoroth")
            {
                string enemy = player == "fp" ? "shadow" : "fp";
                int? locIndex = game.board.FindAllyLocation(ally, player);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    foreach (var enemyAlly in loc.GetAllies(enemy))
                        enemyAlly.TakeDamage(2);
                    msgs.Add("Terror of Gorgoroth: 2 damage to all enemies at this location!");
                }
            }

            // The Balrog of Moria: 3 damage to ALL other allies at location
            if (card.cardName == "The Balrog of Moria")
            {
                int? locIndex = game.board.FindAllyLocation(ally, player);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    foreach (string pid in new[] { "fp", "shadow" })
                    {
                        foreach (var a in loc.GetAllies(pid))
                        {
                            if (a != ally)
                                a.TakeDamage(3);
                        }
                    }
                    msgs.Add("Durin's Bane: 3 damage to ALL other allies at this location!");
                }
            }

            // Dwarven Miner: Prospect
            if (card.cardName == "Dwarven Miner")
                msgs.Add("Prospect: Created a Treasure token! (WP boost later)");

            // Hobbit Bounder: Shirriff
            if (card.cardName == "Hobbit Bounder")
                msgs.Add("Shirriff: Looked at top card of deck.");

            return msgs;
        }

        // --- On-Destroy Effects ---

        /// <summary>
        /// Resolve "When this ally is destroyed" effects.
        /// </summary>
        public List<string> ResolveOnDestroy(BoardAlly ally, string player)
        {
            var msgs = new List<string>();
            CardData card = ally.card;

            // Mordor Orc: add 1 corruption on death
            if (card.cardName == "Mordor Orc")
            {
                game.ring.AddCorruption(1);
                msgs.Add("Mordor Orc's death adds +1 Corruption!");
            }

            // Death-cry keyword
            if (card.keywords != null && card.keywords.Contains("Death-cry"))
            {
                msgs.Add($"{card.cardName}'s Death-cry triggers! (Simplified)");
            }

            return msgs;
        }

        // --- Hero Activated Abilities ---

        /// <summary>
        /// Resolve a Hero's activated ability.
        /// </summary>
        public List<string> ResolveHeroAbility(BoardAlly hero, string player)
        {
            var msgs = new List<string>();
            CardData card = hero.card;
            PlayerManager pState = game.GetPlayerState(player);

            if (card.cardName == "Aragorn, Heir of Isildur")
            {
                hero.tapped = true;
                int? locIndex = game.board.FindAllyLocation(hero, player);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    BoardAlly target = null;
                    foreach (var a in loc.GetAllies(player))
                    {
                        if (a != hero && a.currentToughness < a.card.toughness)
                        {
                            target = a;
                            break;
                        }
                    }
                    if (target != null)
                    {
                        target.Heal(2);
                        msgs.Add($"Aragorn heals {target.card.cardName} for 2 damage!");
                    }
                    else
                    {
                        msgs.Add("No wounded allies at location to heal.");
                    }
                }
                hero.hasUsedAbilityThisTurn = true;
            }
            else if (card.cardName == "Gothmog, Lieutenant of Morgul")
            {
                if (pState.SpendWillpower(2))
                {
                    int? locIndex = game.board.FindAllyLocation(hero, player);
                    if (locIndex != null && locIndex >= 0)
                    {
                        var token = ScriptableObject.CreateInstance<CardData>();
                        TokenFactory.ConfigureOrcToken(token);
                        var tokenAlly = new BoardAlly
                        {
                            card = token,
                            currentToughness = token.toughness,
                            turnEntered = game.turnNumber,
                        };
                        game.board.GetLocation(locIndex.Value).AddAlly(tokenAlly, player, "front");
                        msgs.Add("Gothmog creates an Orc token!");
                        hero.hasUsedAbilityThisTurn = true;
                    }
                    else
                    {
                        msgs.Add("Gothmog must be at a location.");
                    }
                }
                else
                {
                    msgs.Add("Not enough Willpower! Need 2 WP.");
                }
            }
            else if (card.cardName == "Galadriel, Lady of Light")
            {
                hero.tapped = true;
                var drawn = pState.DrawCards(3);
                msgs.Add($"Galadriel's Mirror reveals the future! Drew {drawn.Count} cards.");
                hero.hasUsedAbilityThisTurn = true;
            }
            else if (card.cardName == "Gimli, Son of Gloin")
            {
                hero.tapped = true;
                msgs.Add("Gimli marks an enemy with Grudge! (+2 Power vs that enemy)");
                hero.hasUsedAbilityThisTurn = true;
            }
            else if (card.cardName == "Theoden, King of Rohan")
            {
                hero.tapped = true;
                int? locIndex = game.board.FindAllyLocation(hero, player);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    int rohanCount = 0;
                    foreach (var ally in loc.GetAllies(player))
                    {
                        if (ally.card.faction == Faction.Rohan || ally.card.cardName == "Rider of Rohan")
                            rohanCount++;
                    }
                    msgs.Add($"Theoden rallies {rohanCount} Rohan allies! (+1 Power and Charge)");
                }
                hero.hasUsedAbilityThisTurn = true;
            }
            else if (card.cardName == "Frodo Baggins, Ring-bearer")
            {
                hero.tapped = true;
                if (game.ring.bearer == "fp" && !game.ring.fpActivatedThisTurn)
                {
                    var drawn = pState.DrawCards(2);
                    msgs.Add($"Frodo takes the Ring! Drew {drawn.Count} cards. (No Corruption!)");
                }
                else
                {
                    msgs.Add("Ring already activated or not held by FP.");
                }
                hero.hasUsedAbilityThisTurn = true;
            }
            else if (card.cardName == "Saruman of Many Colors")
            {
                hero.tapped = true;
                int? locIndex = game.board.FindAllyLocation(hero, player);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    if (loc.IsContested)
                    {
                        string enemy = player == "fp" ? "shadow" : "fp";
                        foreach (var enemyAlly in loc.GetAllies(enemy))
                        {
                            msgs.Add($"Saruman's voice weakens {enemyAlly.card.cardName}! (-2 Power)");
                            break;
                        }
                    }
                    else
                    {
                        msgs.Add("Saruman's location is not contested.");
                    }
                }
                hero.hasUsedAbilityThisTurn = true;
            }
            else if (card.cardName == "Gorbag, Captain of the Deeps")
            {
                if (pState.willpowerPool >= 2)
                {
                    CardData goblin = null;
                    foreach (var c in pState.hand)
                    {
                        if (c.cardType == CardType.Ally &&
                            c.creatureTypes != null && c.creatureTypes.Contains("Goblin"))
                        {
                            goblin = c;
                            break;
                        }
                    }
                    if (goblin != null && pState.SpendWillpower(2))
                    {
                        pState.PlayCard(goblin);
                        var goblinAlly = new BoardAlly
                        {
                            card = goblin,
                            currentToughness = goblin.toughness,
                            turnEntered = pState.turnNumber,
                        };
                        bool placed = false;
                        foreach (var loc in game.board.locations)
                        {
                            if (loc.IsContested)
                            {
                                loc.AddAlly(goblinAlly, player, "front");
                                msgs.Add($"Gorbag deploys {goblin.cardName} via Ambush!");
                                placed = true;
                                break;
                            }
                        }
                        if (!placed)
                        {
                            int? heroLoc = game.board.FindAllyLocation(hero, player);
                            if (heroLoc != null && heroLoc >= 0)
                                game.board.GetLocation(heroLoc.Value).AddAlly(goblinAlly, player, "front");
                            msgs.Add($"Gorbag deploys {goblin.cardName}!");
                        }
                        hero.hasUsedAbilityThisTurn = true;
                    }
                    else
                    {
                        msgs.Add("No Goblin in hand or not enough WP!");
                    }
                }
                else
                {
                    msgs.Add("Not enough Willpower! Need 2 WP.");
                }
            }
            else if (card.cardName == "The Golden King of Harad")
            {
                hero.tapped = true;
                pState.AddWillpower(2);
                msgs.Add($"The Golden King grants +2 Willpower! (now {pState.willpowerPool})");
                hero.hasUsedAbilityThisTurn = true;
            }
            else if (card.cardName == "The Witch-king of Angmar")
            {
                hero.tapped = true;
                int? locIndex = game.board.FindAllyLocation(hero, player);
                if (locIndex != null && locIndex >= 0)
                {
                    LocationSlot loc = game.board.GetLocation(locIndex.Value);
                    string enemy = player == "fp" ? "shadow" : "fp";
                    var targets = loc.GetAllies(enemy);
                    if (targets.Count > 0)
                    {
                        var target = targets[0];
                        target.TakeDamage(4);
                        msgs.Add($"Witch-king's Morgul-blade strikes {target.card.cardName}! (4 damage, cannot heal)");
                    }
                    else
                    {
                        msgs.Add("No enemies at location to strike!");
                    }
                }
                hero.hasUsedAbilityThisTurn = true;
            }
            else
            {
                // Generic hero ability
                hero.tapped = true;
                msgs.Add($"{hero.card.cardName} uses their ability (simplified).");
                hero.hasUsedAbilityThisTurn = true;
            }

            return msgs;
        }

        // --- Ring Activation ---

        /// <summary>
        /// Resolve a Free Peoples Ring activation.
        /// </summary>
        public List<string> ResolveRingActivationFP(string choice)
        {
            var msgs = new List<string>();
            RingManager ring = game.ring;

            if (ring.bearer != "fp")
            {
                msgs.Add($"Free Peoples do not bear the Ring! (Bearer: {ring.bearer})");
                return msgs;
            }
            if (ring.fpActivatedThisTurn)
            {
                msgs.Add("Ring already activated this turn! (Once per turn only.)");
                return msgs;
            }

            ring.ActivateFP(choice);
            msgs.Add($"Ring activated! +2 Corruption (now {ring.corruption}/30)");

            switch (choice)
            {
                case "draw":
                    var drawn = game.fpPlayer.DrawCards(2);
                    msgs.Add($"Drew {drawn.Count} cards.");
                    break;
                case "willpower":
                    game.fpPlayer.AddWillpower(2);
                    msgs.Add($"Gained +2 Willpower (now {game.fpPlayer.willpowerPool}).");
                    break;
                case "stealth":
                    msgs.Add("Ring-bearer gains Stealth until end of turn.");
                    break;
                case "bolster":
                    if (game.fpPlayer.hero != null)
                    {
                        int? locIndex = game.board.FindAllyLocation(game.fpPlayer.hero, "fp");
                        if (locIndex != null && locIndex >= 0)
                        {
                            LocationSlot loc = game.board.GetLocation(locIndex.Value);
                            if (loc.locationCard != null)
                            {
                                loc.currentDefense += 2;
                                msgs.Add($"Bolster: {loc.locationCard.cardName} gains +2 Defense!");
                            }
                        }
                    }
                    break;
            }

            return msgs;
        }

        /// <summary>
        /// Resolve a Shadow Ring activation.
        /// </summary>
        public List<string> ResolveRingActivationShadow(string choice)
        {
            var msgs = new List<string>();
            RingManager ring = game.ring;

            if (!ring.CanActivateShadow())
            {
                msgs.Add("Ring already activated this turn!");
                return msgs;
            }
            if (ring.bearer != "shadow")
            {
                msgs.Add("Shadow does not bear the Ring!");
                return msgs;
            }

            ring.ActivateShadow(choice);
            msgs.Add($"Ring activated - Shadow Dominion! +1 Corruption (now {ring.corruption}/30)");

            switch (choice)
            {
                case "drain":
                    game.fpPlayer.willpowerPool = System.Math.Max(0, game.fpPlayer.willpowerPool - 2);
                    game.shadowPlayer.AddWillpower(1);
                    msgs.Add("Drained 2 WP from Free Peoples! Shadow gains +1 WP.");
                    break;
                case "corrupt":
                    ring.AddCorruption(1);
                    msgs.Add($"Inflicted +1 Corruption (now {ring.corruption}/30)");
                    break;
                case "dominate":
                    msgs.Add("Dominated an enemy ally (simplified - not implemented).");
                    break;
                case "fortify":
                    if (game.shadowPlayer.hero != null)
                    {
                        int? locIndex = game.board.FindAllyLocation(game.shadowPlayer.hero, "shadow");
                        if (locIndex != null && locIndex >= 0)
                        {
                            LocationSlot loc = game.board.GetLocation(locIndex.Value);
                            if (loc.locationCard != null)
                            {
                                loc.currentDefense += 3;
                                msgs.Add($"Fortified {loc.locationCard.cardName} with +3 Defense!");
                            }
                        }
                    }
                    break;
            }

            return msgs;
        }
    }
}
