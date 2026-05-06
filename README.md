# Создание AI/ML чат-бота

## Задание 1
[Решение задания 1](Project_template.md)

## Задание 2

- Я взял "мир" The Witcher https://witcher.fandom.com
- Выбрал 31 страницу: [Исходные страницы](initial_pages)
- Собрал [словарь соответствий](terms_map.json), термины подмены сгенерировал используя онлайн LLM
- Выполнил замены [скриптом](terms_replace.py), а затем корректировал вручную, поскольку не удалось предусмотреть все варианты

## Задание 3

### Модель эмбеддингов

- **Название**: `sentence-transformers/all-MiniLM-L6-v2`
- **Размер эмбеддинга**: 384
- **Ссылка**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

### База знаний

- **Источник**: текстовые файлы в папке `./knowledge_base`

### Характеристики индекса

- **Количество чанков**: 66
- **Векторная БД**: FAISS
- **Размер индекса на диске**: ~100 KB

### Время генерации

- **Общее время**: 3.38 секунды
- **Платформа**: Windows 10, CPU (Intel i5)

### Тестирование качества

### Запрос 1: "What happened to Aldric the Ashen Wanderer during the Ashford Purge?"

**Найденные чанки:**
  
  **Результат 1** 
     
    among those slain. Aldric the Ashen Wanderer attempted to protect his companions but was struck with a pitchfork and killed. Rowena of the Copper Grove intervened with a powerful hailstorm spell, saving many lives. Despite these efforts, the exact fa...

  **Результат 2**
     
    The 'Ashford Purge' is a tragic event described in 'The Foreign Wizard' books, recounted by anonymous authors based on eyewitness accounts. Following peace talks with The Iron Dominion, the people of Ashford suffered poverty and resentment due to lac...

  **Результат 3**
  
    comrades. Notably, Aldric the Ashen Wanderer, a prominent Foreign Wizard, brought Elara of the Shifting Sands to the stronghold for refuge and protection, marking a pivotal moment in her development. Observations of the castle include a bridge leadin...


### Запрос 2: "What are Foreign Wizards, and where did they train?"

**Найденные чанки:**

  **Результат 1**

     In the Foreign Wizard universe, magic, or 'the Whisperings', is a multifaceted and powerful force that can be harnessed by various practitioners including Foreign Wizards, the Whisperers, the Root-Speakers, the Bell-Keepers, the Knowing Folk, and Row...

  **Результат 2**

     The Foreign Wizard Iron Ward is a significant artifact within the lore, often referenced across various games and books. In 'The Foreign Wizard' series, it represents a powerful magical item associated with Aldric the Ashen Wanderer, one of its prima...

  **Результат 3**

     Torvin Oak-Scar is a Foreign Wizard, born in 1176 AD during the medieval era. He underwent rigorous training at Hold Grimstone, alongside Aldric the Ashen Wanderer, but his training was cut short due to the Cinderfall Tragedy involving his child, Mir...


### Запрос 3: "What is The Weave-Collapse?"

**Найденные чанки:**

  **Результат 1** 

     Cavalcade', it's available as random loot in various houses around The Sun-Drenched Vale, while in 'Phantom Cavalcade' expansion Crimson Vintage, it can be found in Palebrook's warehouse by the town hall. Despite its complex title, the Weave-Collapse...

  **Результат 2**

     The 'Weave-Collapse' is a historically significant book from The Gilded Quill Studio's Foreign Wizard games, detailing a cosmic event that occurred 1500 years ago during which numerous creatures from parallel universes were accidentally introduced in...

  **Результат 3**

     The concept of The Prime Strand originates from the Shrouded Weavers who created a genetic program to produce an exceptionally gifted child. This "Heir of the Prime Strand" was expected to save the elves from annihilation, but its last carrier, Lira ...

