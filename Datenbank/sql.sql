SELECT 
    users.id, firstName, lastName, image, dateOfRegistration, email
FROM
    users
        LEFT JOIN
    users_has_users ON users.id = users_has_users.asker
        OR users.id = users_has_users.asked
WHERE
    users.id != 1 AND areFriends = 1
        AND (users_has_users.asker = 1
        OR users_has_users.asked = 1)
LIMIT 0 , 10